from django.urls import path
from . import views


urlpatterns=[
    path('',views.index, name='index'),
    path('groups',views.groups,name='groups'),
    path('creategroup',views.creategroup,name='creategroup'),
    path('post',views.post,name='post'),
    path('praise/<int:praise_id>',views.praise,name='praise'),
]