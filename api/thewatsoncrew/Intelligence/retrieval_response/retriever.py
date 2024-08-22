from pydantic import BaseModel, Field
from typing import Any, Dict, List, Union, Optional, Tuple
import json, os
from llama_index.core.retrievers import VectorIndexRetriever
from Intelligence.node_processing.store import Vec_Store
from llama_index.core import get_response_synthesizer
from Intelligence.utils.misc_utils import logger, pr
from Intelligence.retrieval_response.templates import text_qa_template, refine_template, translation_template
from llama_index.core import PromptTemplate
from llama_index.core.postprocessor import SimilarityPostprocessor, TimeWeightedPostprocessor
from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine
from collections import defaultdict
from llama_index.core.schema import NodeWithScore
import yaml
from Intelligence.utils.llm_utils import Settings
from llama_index.core import  VectorStoreIndex
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.response_synthesizers.factory import BaseSynthesizer
from llama_index.retrievers.bm25 import BM25Retriever

class Retriever(VectorIndexRetriever):    
    def __init__(
        self,
        index_path: str, 
        config_file_path: str, 
        verbose: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize params."""
        self._index =  Vec_Store.get_vectorstore(os.path.join('Intelligence/vector_stores', index_path))
        
        with open(config_file_path, 'r') as f:
            config = yaml.safe_load(f) if config_file_path.endswith(".yaml") else json.load(f)

        retrieval_settings = config.get("retrieval", {})
        self.retrieval_settings = retrieval_settings if isinstance(retrieval_settings, dict) else {}

        super().__init__(
            index=self._index,
            verbose= verbose, 
        )

    def get_retriever(self):
        self.vec_retriever  = VectorIndexRetriever(
                                                index=self._index,
                                                **self.retrieval_settings['instance_attr']
                                            )
    
    def retrieve(self, query:str):
        self.get_retriever()
        nodes = self.vec_retriever.retrieve(query)
        # bm25_results = BM25Retriever.from_defaults(nodes=[node.node for node in nodes], 
        #                                            verbose=True, similarity_top_k=20).retrieve( query)
        # sorted_results = sorted(bm25_results, key=lambda x: x.score, reverse=True)
        return nodes
    

class ResponseSynthesizer(BaseModel):
    additional_attributes: Dict[str, Any] = Field(default_factory=dict)
    retriever : Retriever = None
    response_synthesizer: BaseSynthesizer = None
    query_engine : RetrieverQueryEngine = None
    node_post_processors: List[BaseNodePostprocessor] = []
    
    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def initialize(cls, config_file_path: str, retriever:Retriever) -> "ResponseSynthesizer":

        with open(config_file_path, 'r') as f:
            config = yaml.safe_load(f) if config_file_path.endswith(".yaml") else json.load(f)

        response_synthesis_settings = config.get("response_synthesis", {})

        # Ensure settings are dictionaries
        response_synthesis_settings = response_synthesis_settings if isinstance(response_synthesis_settings, dict) else {}

        return cls(
            additional_attributes={
                "response_synthesis": response_synthesis_settings,
            } , 
            retriever = retriever
        )
    
    def get_response_synthesizer(self, response_tone : str = 'assistant'):
        logger.critical(f"tone : {self.additional_attributes['response_synthesis']['response_tone']}")
        text_qa_prompt = PromptTemplate(text_qa_template).partial_format(tone_name = response_tone)
        refine_prompt = PromptTemplate(refine_template).partial_format(tone_name=response_tone)
        
        self.response_synthesizer = get_response_synthesizer(
            llm=Settings.llm , 
            text_qa_template=text_qa_prompt,
            refine_template=refine_prompt,
            # use_async=False,
            # streaming=False,
            **self.additional_attributes['response_synthesis']['instance_attr']
        ) 
           
        return self.response_synthesizer
    
    def get_node_post_processors(self):
        self.node_post_processors = [
                        SimilarityPostprocessor(similarity_cutoff=0.6) ,
                        # TimeWeightedPostprocessor(
                        #     time_decay=0.5, time_access_refresh=False, top_k=1
                        # )
                ]
        return self.node_post_processors
    
    def get_query_engine(self):
        self.get_response_synthesizer()
        self.get_node_post_processors()
            
        self.query_engine = RetrieverQueryEngine(
                                retriever=self.retriever,  # passing retriever object itself
                                # response_synthesizer=self.response_synthesizer,
                                node_postprocessors=self.node_post_processors,
                            )
        
    def respond_query(self, query:str)-> Tuple[str, Dict[str, Union[List, str]]]:
        self.get_query_engine()
        try:
            response = self.query_engine.query(query)
            logger.debug(f'Extracted {len(response.source_nodes)} similar nodes')
            aggregated_metadata = self.aggregate_metadata(response.source_nodes)
            return response.response ,  aggregated_metadata 
        except Exception as e:
            logger.error(e)
            return 'Sorry, I could not find any relevant information.' , {}
        

    def aggregate_metadata(self, nodes: List[NodeWithScore]):
        '''
        currently using following as metadata:
           - source (node_id) to store link/ reference to information
           - unique important keywords across all nodes
           - image_links across all nodes
        '''

        agg_metadata = defaultdict(set)
        
        for node in nodes:
            meta:Dict[str, Union[List, str]] = node.metadata
            keywords = meta['key_words'].split(', ')
            for w in keywords:
                agg_metadata['key_words'].add(w)
            
            agg_metadata['sources'].add(meta['source'])
            
            for img_path in meta['imgs'].split('\n'):
                agg_metadata['imgs'].add(img_path)
                
        agg_metadata['key_words'] = list(agg_metadata['key_words'])
        agg_metadata['sources'] = list(agg_metadata['sources'])
        agg_metadata['imgs'] = list(agg_metadata['imgs'])
        
        # logger.debug(f'Aggregated metadata : {agg_metadata}')
        return agg_metadata
    
    
    
# Ret = Retriever(config_file_path = 'Intelligence/configs/retrieval.yaml', index_path = 'blood_pressure_medical_db')
# # x = Ret.retrieve('share some details on cancer?')
# # x = A.respond_query('share some details on cancer?')
# # print(x)

# s = ResponseSynthesizer.initialize(config_file_path='Intelligence/configs/retrieval.yaml', 
#                                    retriever=Ret)
# x = s.respond_query('Symptoms of high blood pressure.')
# logger.info(x)

