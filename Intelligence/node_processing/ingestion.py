from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.extractors import TitleExtractor, QuestionsAnsweredExtractor
from llama_index.core.ingestion import IngestionPipeline, IngestionCache
from llama_index.core import Document
from typing import Union, List
from Intelligence.utils.misc_utils import pr
from Intelligence.utils.llm_utils import Settings
from Intelligence.node_processing.custom_extractors import DescriptiveKeywords
from Intelligence.node_processing.store import Vec_Store
from Intelligence.node_processing.web_scrapper import Web_Scrapper
import json 

class Pipeline:
    
    def __init__(self, chunk_size=175, chunk_overlap=45):
        self.ingestion = IngestionPipeline(
            transformations=[
                
                SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap),  # https://docs.llamaindex.ai/en/stable/api_reference/node_parsers/token_text_splitter/
                # TitleExtractor(),
                # DescriptiveKeywords(seperator='__', 
                #                     index = Vec_Store.get_vectorstore(path = 'vector_stores/descriptive_prefixes')),
                Settings.embed_model,
            ]
        )

    def run_ingestion(self, documents:Union[List[Document]]):
        nodes = self.ingestion.run(documents=documents, in_place=False, show_progress=True)
        return nodes
    
    def ingest_webdata_to_vecdb(self, path , name:str = 'medical', is_persistent:bool = True):
        with open(path, 'r') as f:
            web_links = [w.strip() for w in f.readlines()]
                    
        unsuccessful_trials = []
        index = Vec_Store.get_vectorstore(path=f'../Intelligence/vector_stores/{name}_db', is_ephemeral = not is_persistent)
        
        for link in web_links:
            scrapper = Web_Scrapper(str(link))
            try : 
                docs = scrapper.create_docs()
                assert len(docs) > 0, 'No documents found'
                pr.green(f'Link scraped {pr.tick}', delimiter='\t')

            except Exception as e:
                pr.red(f'Error in scraping : {e} {pr.cross}')
                d = {
                    'source_type' : 'weblink' ,
                    'source' : link,
                    'issue' : 'scraping_error' ,
                    'error' : str(e) ,
                }
                unsuccessful_trials.append(d)
                continue
            try:
                pr.yellow(len(docs))
                nodes = self.run_ingestion(docs)
                pr.green(f'Nodes extracted {pr.tick}', delimiter='\t')
                index.insert_nodes(nodes)
                pr.green(f'Nodes inserted {pr.tick}')
            except Exception as e :
                pr.red(f'Error in ingestion : {e}  {pr.cross}')
                d = {
                    'source_type' : 'weblink' ,
                    'source' : link,
                    'issue' : 'ingestion_error' ,
                    'error' : str(e) ,
                }
                unsuccessful_trials.append(d)
        
        if len(unsuccessful_trials)>0:
            pr.red(f'Saving unsuccessful trials in : ../Intelligence/data_sources/unsuccessful_trials_{name}.json')
            with open(f'../Intelligence/data_sources/unsuccessful_trials_{name}.json', 'w') as f:
                json.dump(unsuccessful_trials, f)
        else:
            pr.green('<--- All links scraped and ingested successfully --->')
            