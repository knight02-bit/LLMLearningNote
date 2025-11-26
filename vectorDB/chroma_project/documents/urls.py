from django.urls import path
from . import views

urlpatterns = [
    path("", views.add_documents, name="add_documents"),
]
