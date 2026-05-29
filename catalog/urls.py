from django.urls import path
from . import views

urlpatterns = [
        path('', views.index, name='index'),
        #  captures the URL text and passes it to your view
        path('origin//', views.elements_by_origin, name='elements_by_origin'),
]
