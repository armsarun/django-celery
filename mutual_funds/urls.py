from django.urls import path

from mutual_funds.views import index, AddIsin, Visualizer

urlpatterns = [
    path('', index, name='index'),
    path('addisin', AddIsin.as_view(), name='addisin'),
    path('mutual-fund/<slug:isin>', Visualizer.as_view(), name='viewisin')
]