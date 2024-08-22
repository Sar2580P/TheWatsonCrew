from typing import List
from .dummy_data import CONERSE_AI , INSIGHT_AI

def llm_made_links_knowledge_base(links:List[str]):
    print(links)
    return "update knowledge base"            

def llm_converse_ai_readme():
    return CONERSE_AI

def llm_insight_ai_data():
    return INSIGHT_AI
