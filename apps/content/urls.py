from django.urls import path

from . import views

urlpatterns = [
    path("projects/", views.project_list, name="project_list"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    path("blog/", views.post_list, name="post_list"),
    path("blog/<slug:slug>/", views.post_detail, name="post_detail"),
    path("articles/", views.article_list, name="article_list"),
    path("articles/<slug:slug>/", views.article_detail, name="article_detail"),
]
