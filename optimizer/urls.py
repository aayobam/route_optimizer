from django.urls import path
from .import views


urlpatterns = [
    path('data-source/', views.data_source_table_view, name='data_source'),
    path('optimize-route/', views.optimize_route_view, name='optimize_route'),
]
