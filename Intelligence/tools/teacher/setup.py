from pydantic import BaseModel, field_validator
from pathlib import Path
from typing import Optional
from Intelligence.node_processing.web_scrapper import Web_Scrapper
from Intelligence.node_processing.ingestion import Pipeline
from Intelligence.utils.misc_utils import pr
from llama_index.core.schema import Document, TextNode, BaseNode
from typing import List, ClassVar, Dict
from tqdm import tqdm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from Intelligence.utils.templates import COMBINE_INFO_TEMPLATE, QUIZ_TEMPLATE
from llama_index.core.prompts import PromptTemplate
from Intelligence.utils.llm_utils import Settings
from Intelligence.utils.misc_utils import logger, pr
import asyncio
import ast
from collections import defaultdict

class ReadingInfo(BaseModel):
    file_path: Path
    base_dir: Path = Path('/home/sarvagya/cleverchat/Intelligence/tools/teacher')
    name : str = 'teacher_knowledge_base'
    combine_info_template:str = COMBINE_INFO_TEMPLATE
    content: Optional[str] = None
    scrapper :ClassVar[Web_Scrapper] = Web_Scrapper()
    chunk_size:int=250
    chunk_overlap:int=40
    aggregated_notes_collection: List[str] = None
    aggregate_metadata_collection:Dict[str, List] = None
    quiz_collection: List[Dict] = None
    quiz_template: str = QUIZ_TEMPLATE
    
    @field_validator('file_path', mode='before')
    def file_must_exist(cls, v: Path):
        if not v.is_file():
            raise ValueError('File does not exist.')
        if v.suffix != '.txt':
            raise ValueError('File must be a .txt file.')
        return v
    
    def create_knowledgebase(self)-> List[Document]:
        # scrape the links 
        with open(self.file_path, 'r') as f:
            web_links = [w.strip() for w in f.readlines()]
        unsuccessful_trials = []
        final_docs = []
        
        for link in tqdm(web_links, desc='Scraping links'):
            self.scrapper.url = link
            try : 
                docs = self.scrapper.create_docs()
                final_docs.extend(docs)
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

        return final_docs
    
    def create_embeddings(self)-> List[TextNode]:

        transform_pipeline = Pipeline(chunk_size=self.chunk_size, 
                                      chunk_overlap=self.chunk_overlap)
        embedded_nodes = transform_pipeline.run_ingestion(self.create_knowledgebase())

        for i, embedded_node in enumerate(embedded_nodes):
            embedded_node.metadata['rank'] = i
        return embedded_nodes

    def get_clustering(self):
        embedded_nodes = self.create_embeddings()

        # Step 2: Perform DBScan clustering
        embeddings = np.array([node.embedding for node in tqdm(embedded_nodes, 
                                                               desc='Assembling embeddings for clustering')])

        # Step 2: Dimensionality Reduction (Optional but recommended)
        pca = PCA(n_components=100)  # Reduce to 50 dimensions
        reduced_embeddings = pca.fit_transform(embeddings)

        # Step 3: Clustering (DBSCAN)
        clustering = DBSCAN(eps=0.5, min_samples=2, metric="cosine").fit(reduced_embeddings)

        # Step 3: Create DataFrame for clustering results
        labels = clustering.labels_
        ids = range(len(embedded_nodes))
        ranks = [node.metadata['rank'] for node in embedded_nodes]
        content = [node.text for node in embedded_nodes]
        meta_data = [node.metadata for node in embedded_nodes]
        df = pd.DataFrame({
            'id': ids,
            'label': labels,
            'rank': ranks, 
            'content': content, 
            'metadata': meta_data,
        })
        
        # Step 4: Save DataFrame to CSV file
        save_path = self.base_dir / 'clustering_results.csv'
        df.to_csv(save_path, index=False)
        print(f"CSV file saved: {save_path}")

        # tsne_embedded = TSNE(n_components=3, random_state=42).fit_transform(reduced_embeddings)
        
        # fig = plt.figure(figsize=(12, 10))
        # ax = fig.add_subplot(111, projection='3d')
        # scatter = ax.scatter(tsne_embedded[:, 0], tsne_embedded[:, 1], tsne_embedded[:, 2], c=labels, cmap='viridis', alpha=0.5)
        
        # ax.set_title('3D TSNE Plot of Clustering')
        # ax.set_xlabel('TSNE Component 1')
        # ax.set_ylabel('TSNE Component 2')
        # ax.set_zlabel('TSNE Component 3')
        
        # legend1 = ax.legend(*scatter.legend_elements(), title="Clusters")
        # ax.add_artist(legend1)
        
        # plt.savefig(self.base_dir/'clustering_tsne_plot_3d.png')

    
    def ordering_content(self, df:pd.DataFrame)->List:
        # Step 1: Assign global ordering to labels based on minimum rank, breaking ties with maximum rank
        label_ordering :List = (
            df.groupby('label')['rank']
            .agg(['min', 'max'])
            .sort_values(by=['min', 'max'])
            .index.tolist()
        )
    
        # Step 2: Create a list to store ordered contents
        ordered_contents = []
        ordered_metadata = []
            # Step 3: Iterate through all the labels in global order
        for label in tqdm(label_ordering, desc = 'Ordering information chunks'):
            label_content = df[df['label'] == label]['content'].tolist()
            combined_content = f"\n{'-'*75}\n".join(label_content)
            combined_metadata = self.aggregate_metadata(df[df['label'] == label]['metadata'].tolist())
            ordered_contents.append(combined_content)
            ordered_metadata.append(combined_metadata)

        self.aggregate_metadata_collection = ordered_metadata

        return ordered_contents, ordered_metadata
    
    def aggregate_metadata(self, metadata:List[Dict])->Dict:
        '''
        currently using following as metadata:
           - source (node_id) to store link/ reference to information
           - unique important keywords across all nodes
           - image_links across all nodes
        '''

        agg_metadata = defaultdict(set)
        
        for meta in metadata:
            meta = ast.literal_eval(meta)
            keywords = meta['key_words'].split(', ')
            for w in keywords:
                agg_metadata['key_words'].add(w)
            
            agg_metadata['sources'].add(meta['source'])
            external_ref = meta['external_ref']
            
            for img_path in meta['imgs'].split('\n'):
                agg_metadata['imgs'].add(img_path)
                
        agg_metadata['key_words'] = list(agg_metadata['key_words'])
        agg_metadata['sources'] = list(agg_metadata['sources'])
        agg_metadata['imgs'] = list(agg_metadata['imgs'])
        
        # logger.debug(f'Aggregated metadata : {agg_metadata}')
        return agg_metadata
    
    async def create_notes(self, contents: List[str]) -> List[str]:
        import asyncio

        async def fetch_note(content: str, template:str) -> str:
            full_prompt = PromptTemplate(template).format(info= content)

            note = Settings.llm.complete(full_prompt).text.strip()
            return note
        try:
            # Create a list of tasks for asynchronous fetching of notes
            tasks = [fetch_note(content, self.combine_info_template) for content in tqdm(contents[:2], desc = 'making notes using LLM')]
            
            # Await the completion of all tasks
            self.aggregated_notes_collection = await asyncio.gather(*tasks)
            return self.aggregated_notes_collection
        except Exception as e:
            pr.red(e)
            return
            
    
    async def create_quiz(self, contents: List[BaseNode]= None) -> List[Dict]:
        async def fetch_docs(content: str, template:str) -> str:
            full_prompt = PromptTemplate(template).format(info= content)
            response = f'''{Settings.llm.complete(full_prompt)}'''
            try : 
                quiz = ast.literal_eval(response[response.find('[')  : response.rfind(']')+1])
                return quiz
            except Exception as e:
                logger.error(f'Error in creating quiz :  {response}')
                return []

        if contents is None:
            contents = self.aggregated_notes_collection
        # Create a list of tasks for asynchronous fetching of notes
        tasks = [fetch_docs(content, self.quiz_template) for content in tqdm(contents, desc = 'making quiz using LLM')]
        
        # Await the completion of all tasks
        quiz_list = await asyncio.gather(*tasks)
        self.quiz_collection = []
        for quiz in quiz_list:
            self.quiz_collection.extend(quiz)
        return self.quiz_collection
    
    

# import asyncio
# KB_Creator = ReadingInfo(file_path=Path('Intelligence/tools/teacher/links.txt'))
# x = a.ordering_content(pd.read_csv('Intelligence/tools/teacher/clustering_results.csv'))
# y = asyncio.run(a.create_notes(x[:1]))
# z = asyncio.run(a.create_quiz(y))
# pr.green(y)
# pr.yellow(z)
        
    
    