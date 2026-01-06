from django.urls import path

from . import views

urlpatterns = [
    path("", views.index_view, name="index"),
    path("api/text-to-speech/", views.text_to_speech_view, name="text_to_speech"),
]
