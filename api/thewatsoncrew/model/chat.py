from .dummy_data import CHAT_AI
from api.thewatsoncrew.Intelligence.agents.agent_tree import ROOT
from typing import List, Dict

def llm_chat_response(message : str)-> List[Dict]:
    ROOT.input = message
    instance_list = ROOT.dag_response()
    response = []
    for instance in instance_list:
        response.append({
            'response' : instance.output
        }.update(instance.metadata))
    return response