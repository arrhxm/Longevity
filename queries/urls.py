from django.urls import path
from .views import client_queries, create_query, query_detail, update_query_status, dietitian_queries

urlpatterns = [
    path("my/", client_queries, name="client_queries"),
    path("new/", create_query, name="create_query"),
    path("<int:query_id>/", query_detail, name="query_detail"),
    path("<int:query_id>/status/", update_query_status, name="update_query_status"),
    path("manage/", dietitian_queries, name="dietitian_queries"),
]
