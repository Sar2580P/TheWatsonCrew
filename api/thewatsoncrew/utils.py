from rest_framework.response import Response
from .model.links_knowledge import llm_made_links_knowledge_base , llm_converse_ai_readme , llm_insight_ai_data, get_test_paper_evaluate_ai
from .model.chat import llm_chat_response

def success_response(data):
    return Response({'response': data , 'status': 200, 'message': 'Success'})

def failed_response(data):
    return Response({'response': data , 'status': 500, 'message': 'Failed'} , status=500)

def post_link_knowledge_base(knowledge_base):
    try:
        answer = llm_made_links_knowledge_base(knowledge_base)
        return success_response(answer)
    except Exception as e:
        return failed_response(str(e))

def get_converse_ai_readme():
    try:
        answer = llm_converse_ai_readme()
        return success_response(answer)
    except Exception as e:
        return failed_response(str(e))

def get_insight_ai_data():
    try:
        answer = llm_insight_ai_data()
        return success_response(answer)
    except Exception as e:
        return failed_response(str(e))

def get_evaluate_ai():
    try:
        answer = get_test_paper_evaluate_ai()
        return success_response(answer)
    except Exception as e:
        return failed_response(str(e))

def post_chat(message, status=201):
    try:
        print(message)
        answer = llm_chat_response(message)
        return success_response(answer)
    except Exception as e:
        return failed_response(str(e))
