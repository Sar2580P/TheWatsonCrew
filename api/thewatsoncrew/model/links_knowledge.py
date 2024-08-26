from typing import List
from .dummy_data import CONERSE_AI , INSIGHT_AI, TEST_PAPER_EVALUATE_AI
from Intelligence.tools.teacher.setup import ReadingInfo
import pandas as pd
import asyncio
import json 

KB_Creator = ReadingInfo.from_config(config_path='../Intelligence/configs/tools/teacher.yaml')

def llm_made_links_knowledge_base(links:List[str]):
    # KB_Creator.get_clustering(web_links=links)
    KB_Creator.ordering_content(pd.read_csv('../Intelligence/tools/teacher/clustering_results.csv'))
    return "updated knowledge base"            

def llm_insight_ai_data():
    # return INSIGHT_AI
    return KB_Creator.create_video_frames()

def llm_converse_ai_readme():
    # return CONERSE_AI
    print('Helloe world')
    response =  asyncio.run(KB_Creator.create_notes(max_notes=3))
    print(response , '-------------------------------------------------')
    return response
    
    
def get_test_paper_evaluate_ai():
    # return TEST_PAPER_EVALUATE_AI
    response =  asyncio.run(KB_Creator.create_quiz())
    return response