from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRoutes, name="routes"),
    path("thewatsoncrew/link_knowledge_base/", views.link_knowledge_base, name="link_knowledge_base"),
    path("thewatsoncrew/blogs_ai/", views.blogs_ai, name="blogs_ai"),
    path("thewatsoncrew/watch_ai/", views.watch_ai, name="watch_ai"),
    path("thewatsoncrew/evaluate_ai/", views.evaluate_ai, name="evaluate_ai"),
    path("thewatsoncrew/chat/", views.chat, name="chat"),
]