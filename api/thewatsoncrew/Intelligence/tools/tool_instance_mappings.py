from Intelligence.tools.leaf_nodes import *
from langchain.tools import BaseTool


tool_instance_mapping:dict[str, BaseTool] = {
    'diabetes_doctor_tool'.upper(): DiabetesDoctor() , 
    'blood_pressure_doctor_tool'.upper(): BPDoctor() ,
     
    'finance_advisor_tool'.upper(): FinanceAdvisor() , 
    
    'get_similar_work_items_tool'.upper() : GetSimilarWorkItems(), 
    'summarize_objects_tool'.upper() : Summarize(),
    'prioritize_objects_tool'.upper() : Prioritize(), 
    'search_object_by_name_tool'.upper() : SearchObjectByName(), 
    'create_actionable_tasks_from_text_tool'.upper() : CreateActionableTasksFromText(),
}