from llama_index.core.extractors import BaseExtractor
from typing import List, Dict, Sequence , Tuple, Optional, Any, cast
from pydantic import Field
from llama_index.core.schema import BaseNode, TextNode , Document
from llama_index.core import PromptTemplate
from llama_index.core.async_utils import DEFAULT_NUM_WORKERS, run_jobs
from llama_index.core.llms.llm import LLM
from llama_index.core.service_context_elements.llm_predictor import (
    LLMPredictorType,
)
import ast
from Intelligence.utils.llm_utils import Settings
from Intelligence.utils.templates import DEFAULT_NER_TEMPLATE
import re
from Intelligence.node_processing.store import Vec_Store, VectorStoreIndex

class DescriptiveKeywords(BaseExtractor):
    """DescriptiveKeywords extractor. Useful for extracting complex named entities from text and 
    replace them with simple descriptive names.
    
    Args:
        llm (Optional[LLM]): LLM
        nodes (int): number of nodes from front to use for extraction
        node_template (str): template for node-level title clues extraction
    """

    is_text_node_only: bool = False  # can work for mixture of text and non-text nodes
    llm: LLMPredictorType = Field(description="The LLM to use for generation.")
    nodes: int = Field(
        default=5,
        description="The number of nodes to extract titles from.",
        gt=0,
    )
    node_template: str = Field(
        default=DEFAULT_NER_TEMPLATE,
        description="The prompt template to extract named entites from text.",
    )
    seperator : str = Field(
        default='__' ,
        description="The seperator to use for combining the description and entity"
    )
    # combine_template: str = Field(
    #     default=DEFAULT_TITLE_COMBINE_TEMPLATE,
    #     description="The prompt template to merge titles with.",
    # )
    index : VectorStoreIndex = Field(
        default = Vec_Store.get_vectorstore(path = 'vector_stores/descriptive_prefixes') , 
        description = "The vector store to store the descriptive prefixes"
    )

    def __init__(
        self,
        llm: Optional[LLM] = None,
        # TODO: llm_predictor arg is deprecated
        llm_predictor: Optional[LLMPredictorType] = None,
        nodes: int = 1,
        node_template: str = DEFAULT_NER_TEMPLATE,
        # combine_template: str = DEFAULT_TITLE_COMBINE_TEMPLATE,
        num_workers: int = DEFAULT_NUM_WORKERS,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        if nodes < 1:
            raise ValueError("num_nodes must be >= 1")
        super().__init__(
            llm=llm or llm_predictor or Settings.llm,
            nodes=nodes,
            node_template=node_template,
            # combine_template=combine_template,
            num_workers=num_workers,
            **kwargs,
        )

    @classmethod
    def class_name(cls) -> str:
        return "DescriptiveKeywords"
        
    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
        extracted_keywords : List[List[Tuple]] = await self.aner(nodes)
        keywords = []
        for i, node in enumerate(nodes):
            if isinstance(node, TextNode):
                e = ast.literal_eval(extracted_keywords[i])
                node.text = await self.update_text(node.text, e) 
                keywords.append({"keywords":', '.join([x[1].split(self.seperator)[1] for x in e]) })
        return keywords
    
    async def aner(self, nodes: Sequence[BaseNode]) -> List[List[Tuple]]:
        ner_jobs = [
            self.llm.apredict(
                PromptTemplate(template=self.node_template, sep = self.seperator ,
                               text=cast(TextNode, node).text),
                
            )
            for node in nodes
        ]
        return await run_jobs(
            ner_jobs, show_progress=self.show_progress, workers=self.num_workers
        )
    
    async def update_text(self, text: str, keywords: List[Tuple]) -> str:
        for keyword in keywords:
            original_keyword = keyword[1].split(self.seperator)[1]
            descriptive_prefix = keyword[1].split(self.seperator)[0]
            substitute = keyword[1]

            await self.add_prefix_to_vectorestore(descriptive_prefix = descriptive_prefix , 
                                                  named_entity = original_keyword)
            
            # Prepare the original_keyword for regex matching by replacing '_' with '\s'
            original_keyword_pattern = re.compile(original_keyword.replace('_', '\s+'))
            # Use the pattern to replace occurrences in the text
            text = original_keyword_pattern.sub(substitute, text)
        return text
    
    async def add_prefix_to_vectorestore(self, descriptive_prefix: str , named_entity : str):
        
        retriever = self.index.as_retriever(similarity_top_k = 1)
        nodes = retriever.retrieve(descriptive_prefix)

        if len(nodes)> 0 and nodes[0].score > 0.85:
            # add named entity to keywords of current node
            node = nodes[0].node
            node.metadata['keywords'] = node.metadata.get('keywords', '') +'\t'+ named_entity
        else :
            # create a new node with descriptive prefix as title and named entity as keywords
            node = Document(text = descriptive_prefix , metadata = {'keywords': named_entity})
            self.index.insert_nodes([node])        


# text = '''
# The 55-year-old male patient presented with symptoms of Myocarditis and subsequently developed Atrial Fibrillation. 
# He was administered Amiodarone to manage the arrhythmia. Additionally, his history revealed Type 2 Diabetes Mellitus, 
# controlled with Metformin and occasional use of Insulin Glargine. During the examination, signs of Chronic Obstructive Pulmonary Disease (COPD) were noted, for which he was already on Tiotropium. Recently, he experienced severe joint pain attributed to Rheumatoid Arthritis, 
# being treated with Methotrexate and Etanercept. To address his Hypertension, Amlodipine and Lisinopril were prescribed. Moreover, the patient had a previous episode of Deep Vein Thrombosis (DVT), currently managed with Warfarin. In light of his persistent Gastroesophageal Reflux Disease (GERD), he was taking Omeprazole.
# A comprehensive review of his medication regimen was essential to prevent potential drug interactions and ensure optimal therapeutic outcomes, given the complexity of his multiple chronic conditions.'''

# node = TextNode(text=text)
# extractor = DescriptiveKeywords(seperator='__', index = Vec_Store.get_vectorstore(path = 'vector_stores/descriptive_prefixes'))
# # # print(cast(TextNode, node).text)
# # # print(node.text)
# print(extractor.extract([node]))
# print('\n\n\n' , node.text)
# print('\n\n\n' , node.metadata)