from pydantic import BaseModel, field_validator
from pathlib import Path
from typing import Optional
from Intelligence.node_processing.web_scrapper import Web_Scrapper
from Intelligence.node_processing.ingestion import Pipeline
from Intelligence.utils.misc_utils import pr
from llama_index.core.schema import Document, TextNode, BaseNode
from typing import List, ClassVar, Dict, Tuple
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
from Intelligence.utils.misc_utils import logger, pr, read_yaml
import asyncio
import ast, json, re
from collections import defaultdict
from collections import OrderedDict

class ReadingInfo(BaseModel):
    config : Dict = None
    file_path: Path=None
    base_dir: Path = None
    name : str = None
    chunk_size:int = None
    chunk_overlap:int = None
    scrapper :ClassVar[Web_Scrapper] = Web_Scrapper()
    content: Optional[str] = None
    aggregated_notes_collection: List[str] = None
    aggregate_metadata_collection:Dict[str, List] = None
    quiz_collection: List[Dict] = None
    combine_info_template:str = COMBINE_INFO_TEMPLATE
    quiz_template: str = QUIZ_TEMPLATE
    
    @classmethod
    def from_config(cls, config_path:str)->'ReadingInfo':
        config = read_yaml(config_path)
        instance = cls(**config)
        instance.config = config
        return instance
    
    def create_knowledgebase(self , web_links:List[str]=None)-> Dict[int, List[Document]]:
        if not web_links:
            logger.debug('No web-links provided, using default from links.txt')
            web_links = [w.strip() for w in open(self.file_path, 'r').readlines()]


        unsuccessful_trials , final_docs = [] , {}
        src_label = 0
        
        for link in tqdm(web_links, desc='Scraping links'):
            self.scrapper.url = link
            try : 
                docs = self.scrapper.create_docs()
                assert len(docs) > 0, 'No documents found'
                final_docs[src_label] = docs
                src_label+=1
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
    
    def create_embeddings(self , web_links:List[str]=None)-> List[TextNode]:
        logger.debug('Creating embeddings ...')
        transform_pipeline = Pipeline(chunk_size=self.chunk_size, 
                                      chunk_overlap=self.chunk_overlap)
        
        labelled_docs = self.create_knowledgebase(web_links)
        final_docs = []
        for label, docs in labelled_docs.items():
            rank = 0
            for doc in docs:
                doc.metadata['rank'] = rank   # corresponds to the rank of doc within the source url
                doc.metadata['document_label'] = label   # the label corresponds to the url from which the document was scraped
                final_docs.append(doc)
                rank+=1
            
        return transform_pipeline.run_ingestion(final_docs)


    def get_clustering(self, web_links:List[str]=None):
        logger.debug('Clustering the information chunks ...')
        embedded_nodes = self.create_embeddings(web_links=web_links)

        # Step 2: Perform DBScan clustering
        embeddings = np.array([node.embedding for node in tqdm(embedded_nodes, 
                                                               desc='Assembling embeddings for clustering')])

        # Step 2: Dimensionality Reduction (Optional but recommended)
        pca = PCA(n_components=self.config['n_components'] ,whiten=self.config['whiten'])  # Reduce to 50 dimensions
        reduced_embeddings = pca.fit_transform(embeddings)

        # Step 3: Clustering (DBSCAN)
        clustering = DBSCAN(eps=self.config['eps'], min_samples=self.config['min_samples'], 
                            metric=self.config['metric']).fit(reduced_embeddings)

        # Step 3: Create DataFrame for clustering results
        labels = clustering.labels_
        ids = range(len(embedded_nodes))
        ranks = [node.metadata['rank'] for node in embedded_nodes]
        source_labels = [node.metadata['document_label'] for node in embedded_nodes]
        content = [node.text for node in embedded_nodes]
        meta_data = [node.metadata for node in embedded_nodes]
        df = pd.DataFrame({
            'id': ids,
            'label': labels,
            'rank': ranks, 
            'source_label': source_labels,
            'content': content, 
            'metadata': meta_data,
        })
        
        # Step 4: Save DataFrame to CSV file
        save_path = self.base_dir / 'clustering_results.csv'
        df.to_csv(save_path, index=False)
        logger.debug(f"clustering CSV file saved: {save_path}")

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

    
    def ordering_content(self, df:pd.DataFrame)->Tuple[List ,List]:
        # Step 1: Assign global ordering to labels based on minimum rank, breaking ties with maximum rank
        label_ordering :List = (
            df.groupby('label')['rank']
            .agg(['min', 'max'])
            .sort_values(by=['min', 'max'])
            .index.tolist()
        )
    
        # Step 2: Create a list to store ordered contents
        ordered_contents, ordered_metadata = [], []
        # Step 3: Iterate through all the labels in global order
        for label in tqdm(label_ordering, desc = 'Ordering information chunks'):
            label_content = df[df['label'] == label]['content'].tolist()
            combined_content = f"\n{'-'*75}\n".join(label_content)
            combined_metadata = self.aggregate_metadata(df[df['label'] == label]['metadata'].tolist())
            ordered_contents.append(combined_content)
            ordered_metadata.append(combined_metadata)

        self.aggregate_metadata_collection = ordered_metadata
        self.content = ordered_contents

        return ordered_contents, ordered_metadata
    
    def aggregate_metadata(self, metadata:List[Dict])->Dict:
        agg_metadata = defaultdict(set)
        agg_metadata['external_references'] = {}
        for meta in metadata:
            meta = ast.literal_eval(meta)
            keywords, external_refs = meta['key_words'].split('\n') , meta['external_ref'].split('\n')
            for i in range(len(keywords)):
                agg_metadata['external_references'][keywords[i]] = external_refs[i]
            
            agg_metadata['sources'].add(meta['source'])
            
            for img_path in meta['imgs'].split('\n'):
                agg_metadata['imgs'].add(img_path)
                
        agg_metadata['sources'] = list(agg_metadata['sources'])
        agg_metadata['imgs'] = list(agg_metadata['imgs'])

        return agg_metadata
    
    async def create_notes(self, max_notes:int = 2) -> List[str]:
        
        async def fetch_note(content: str, template:str) -> str:
            full_prompt = PromptTemplate(template).format(info= content)

            note = Settings.llm.complete(full_prompt).text.strip()
            return note
        try:
            pr.purple(len(self.content))
            # Create a list of tasks for asynchronous fetching of notes
            tasks = [fetch_note(content, self.combine_info_template) for content in tqdm(self.content[:max_notes], desc = 'making notes using LLM')]
            
            # Await the completion of all tasks
            self.aggregated_notes_collection = await asyncio.gather(*tasks)
            response = []
            for note, metadata in zip(self.aggregated_notes_collection, self.aggregate_metadata_collection):
                d = {"text" : note}
                d.update(metadata)
                response.append(d)
                
            # with open('../output.json', 'w') as json_file:
            #     json.dump(response, json_file, indent=4)
            return response
        except Exception as e:
            logger.error(str(e))
            return
            
    
    async def create_quiz(self) -> List[Dict]:
        async def fetch_docs(content: str, template:str) -> str:
            full_prompt = PromptTemplate(template).format(info= content)
            response = f'''{Settings.llm.complete(full_prompt)}'''
            try : 
                quiz = ast.literal_eval(response[response.find('[')  : response.rfind(']')+1])
                return quiz
            except Exception as e:
                logger.error(f'Error in creating quiz :  {e}')
                return []

        # Create a list of tasks for asynchronous fetching of notes
        tasks = [fetch_docs(content, self.quiz_template) for content in tqdm(self.aggregated_notes_collection, desc = 'making quiz using LLM')]
        
        # Await the completion of all tasks
        quiz_list = await asyncio.gather(*tasks)
        self.quiz_collection = []
        for quiz in quiz_list:
            self.quiz_collection.extend(quiz)
        return self.quiz_collection
    
    def create_video_frames(self):
        frames = []
        for content , metadata in zip(self.aggregated_notes_collection, self.aggregate_metadata_collection):
            contents = [part for part in re.split(r'(?<!#)##(?!#)', content) if part]

            for sections in contents:
                heading = sections.split('\n')[0].strip()
                section_content = '\n'.join(sections.split('\n')[1:]).strip()
                sub_contents = re.split(r'(?=###)', section_content)

                for sub_content in sub_contents:
                    frames.append({
                        'heading' : heading,
                        'content' : sub_content,
                        'metadata' : metadata
                    })
                    
        json.dump(frames, open(self.base_dir/'video_frames.json', 'w'))
    

if __name__ == '__main__':
    KB_Creator = ReadingInfo.from_config(config_path='../Intelligence/configs/tools/teacher.yaml')
    # w = KB_Creator.get_clustering()
    x = KB_Creator.ordering_content(pd.read_csv('../Intelligence/tools/teacher/clustering_results.csv'))
    y = asyncio.run(KB_Creator.create_notes(max_notes = 2))
    pr.green(y)
    # z = asyncio.run(KB_Creator.create_quiz())
    # # pr.yellow(z)
    # a = KB_Creator.create_video_frames()
    