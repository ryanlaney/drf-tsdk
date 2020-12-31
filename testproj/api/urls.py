from django.urls import path, re_path

from .foo import FooView
from .bar import bar

urlpatterns = [
    path('foo', FooView.as_view({'get': "list", 'post': "create"})),
    path('foo/<int:pk>',
         FooView.as_view({'get': "retrieve", 'post': "update", 'delete': "destroy"})),
    path('bar', bar)
]
