from rest_framework.response import Response
from rest_framework.decorators import api_view
from .utils import post_link_knowledge_base , get_converse_ai_readme , get_insight_ai_data , get_evaluate_ai, post_chat

@api_view(['GET'])
def getRoutes(request):
    routes = [
        {
            'Endpoint': '/thewatsoncrew/link_knowledge_base/',
            'method': 'POST',
            'body': {'links': 'string'},
            'description': 'Link knowledge base'
        },
        {
            'Endpoint': '/thewatsoncrew/converse_ai_readme/',
            'method': 'GET',
            'body': None,
            'description': 'Converse AI readme'
        },
        {
            'Endpoint': '/thewatsoncrew/chat/',
            'method': 'POST',
            'body': {'message': 'string'},
            'description': 'Chat'
        },
        {
            'Endpoint': '/thewatsoncrew/insight_ai_data/',
            'method': 'GET',
            'body': None,
            'description': 'Insight AI data'
        },
        {
            'Endpoint': '/thewatsoncrew/evaluate_ai/',
            'method': 'GET',
            'body': None,
            'description': 'Evaluate AI'
        },
        {
            'Endpoint': '/thewatsoncrew/evaluate_ai/',
            'method': 'POST',
            'body': {'data': 'string'},
            'description': 'Evaluate AI'
        }
    ]
    return Response(routes)

@api_view(['POST'])
def link_knowledge_base(request):
    knowledge_base = request.data['links']
    return post_link_knowledge_base(knowledge_base)

@api_view(['GET'])
def converse_ai_readme(request):
    return get_converse_ai_readme()

@api_view(['GET'])
def insight_ai_data (request):
    return get_insight_ai_data()

@api_view(['GET'])
def evaluate_ai(request):
    return get_evaluate_ai()

@api_view(['POST'])
def chat(request):
    message = request.data['message']
    return post_chat(message)
