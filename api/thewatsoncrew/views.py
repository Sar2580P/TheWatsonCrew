from rest_framework.response import Response
from rest_framework.decorators import api_view
from .utils import *

@api_view(['GET'])
def getRoutes(request):
    routes =[]
    return Response(routes)