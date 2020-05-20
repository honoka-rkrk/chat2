from django.contrib import admin
from .models import Message,Group,Praise,GroupMember

admin.site.register(Message)
admin.site.register(Group)
admin.site.register(Praise)
admin.site.register(GroupMember)
