'''
This file contains actual tools, which only does execution not planning.
'''
from langchain.tools import BaseTool
from typing import Optional, Any 
from Intelligence.retrieval_response.retriever import Retriever, ResponseSynthesizer
from Intelligence.utils.misc_utils import pr
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)

# Medical ------->>>>

class DiabetesDoctor(BaseTool):
    name = "diabetes_doctor_tool".upper()
    description = '''
    - The tool specializes in knowledge related to diabetes/blood sugar disease, symptoms, diagnosis, and treatment.
    '''
    retriever: Retriever = None
    response_generator: ResponseSynthesizer = None
    emoji = "\U00002695\U0000FE0F I am a doctor! 🩺"
    def __init__(self):
        super().__init__()
        self.retriever = Retriever(config_file_path='../Intelligence/configs/retrieval.yaml', index_path='blood_sugar_medical_db')
        self.response_generator = ResponseSynthesizer.initialize(config_file_path='../Intelligence/configs/retrieval.yaml', 
                                                                 retriever=self.retriever)
    
    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Any:
        response, metadata = self.response_generator.respond_query(query)
        return {'tool_response' : response, 
                'response_metadata' : metadata}
    
    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")
    
#_________________________________________________________________________________________________________________________ 

class BPDoctor(BaseTool):
    name = "blood_pressure_doctor_tool".upper()
    description = '''
    - The tool specializes in knowledge related to blood pressure, its symptoms, diagnosis, and treatment.
    '''
    
    retriever: Retriever = None
    response_generator: ResponseSynthesizer = None
    emoji = "\U00002695\U0000FE0F I am a doctor! 🩺"
    def __init__(self):
        super().__init__()
        self.retriever = Retriever(config_file_path='../Intelligence/configs/retrieval.yaml', index_path='blood_pressure_medical_db')
        self.response_generator = ResponseSynthesizer.initialize(config_file_path='../Intelligence/configs/retrieval.yaml', 
                                                                 retriever=self.retriever)
    
    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Any:
       
        response, metadata = self.response_generator.respond_query(query)
        return {'tool_response' : response, 
                'response_metadata' : metadata}
    
    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

#_________________________________________________________________________________________________________________________ 
class FinanceAdvisor(BaseTool):
    name = "finance_advisor_tool".upper()
    description = '''
    - This tool is helpful for queries related to financial matters.
    - The tool specializes in knowledge related to cryptocurrency, stock market, and financial literacy
    '''
    
    retriever: Retriever = None
    response_generator: ResponseSynthesizer = None
    emoji =  "\U0001F4B0 I'm your financial advisor! 💰"
    def __init__(self):
        super().__init__()
        self.retriever = Retriever(config_file_path='../Intelligence/configs/retrieval.yaml', index_path='financial_advisor_db')
        self.response_generator = ResponseSynthesizer.initialize(config_file_path='../Intelligence/configs/retrieval.yaml', 
                                                                 retriever=self.retriever)
    
    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Any:
        response, metadata = self.response_generator.respond_query(query)
        return {'tool_response' : response, 
                'response_metadata' : metadata}
    
    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")
    
# _________________________________________________________________________________________________________________________

class GetSimilarWorkItems(BaseTool):
    name = "get_similar_work_items_tool".upper()
    description = '''
    
    USAGE :
        - Use this tool when you want to get work_items similar to the current work_item.
        - This tool returns a list of similar work_items for the given work_id. 
    '''
    bag_of_words = set(["similar","similar items", "similar work_items", "similar work"])
    
    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Any:
        return {'tool_response' : 'used GetSimilarWorkItems'}
    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

# _________________________________________________________________________________________________________________________

class Summarize(BaseTool):
    name = "summarize_objects_tool".upper()
    description = '''
    - This tool is useful for summarizing purposes.
    - It needs a list of objects as input and returns a summary of the objects. 
    '''
    
    bag_of_words = set(["summary", "summarize", "summarize objects", "summarization"])
    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Any:
        return {'tool_response' : 'used Summarize'}
    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

# _________________________________________________________________________________________________________________________

class Prioritize(BaseTool):
    name = "prioritize_objects_tool".upper()
    description = '''
    - Use this tool when asked to prioritize the objects. 
    '''

    bag_of_words = set(["prioritize", "priority", "prioritize objects", "prioritization"])
    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Any:
        return {'tool_response' : 'used Prioritize'}
    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

# _________________________________________________________________________________________________________________________
  
class SearchObjectByName(BaseTool):
    name = "search_object_by_name_tool".upper()
    description = '''
        The tool is useful to find the id of the object by searching the object name or customer name.
    '''

    bag_of_words = set(["customer", "customer name", "username", "user", "part name"])
    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Any:
        return {'tool_response' : 'used search_object_by_name'}

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")

# _________________________________________________________________________________________________________________________

class CreateActionableTasksFromText(BaseTool):
    name = "create_actionable_tasks_from_text_tool".upper()
    description = '''

    USAGE : 
     - Given a text, extracts actionable insights, and creates tasks for them, which are kind of a work item. '''
    
    bag_of_words = set(["create actionable tasks", "create tasks", "create insights", "plan tasks", "create tasks from text","create"])
    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Any:
        return {'tool_response' : 'used CreateActionableTasksFromText'}
    
    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")