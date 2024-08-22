from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoutes, name="routes"),
    path("thewatsoncrew/link_knowledge_base/", views.link_knowledge_base, name="link_knowledge_base"),
    path("thewatsoncrew/converse_ai_readme/", views.converse_ai_readme, name="converse_ai_readme"),
    path("thewatsoncrew/insight_ai_data/", views.insight_ai_data, name="insight_ai_data"),
    path("thewatsoncrew/evaluate_ai/", views.evaluate_ai, name="evaluate_ai"),
    path("thewatsoncrew/chat/", views.chat, name="chat"),
]