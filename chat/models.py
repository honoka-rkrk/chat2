from django.db import models
from django.contrib.auth.models import User

# Messageクラス
class Message(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_owner')
    group=models.ForeignKey('Group',on_delete=models.CASCADE)
    content=models.TextField(max_length=1000)
    praise_count=models.IntegerField(default=0)
    pub_date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.content)+ '(' +str(self.owner)+ ')'
    
    class Meta:
        ordering = ('-pub_date',)

#Groupクラス
class Group(models.Model):
    owner=models.ForeignKey(User,on_delete=models.CASCADE,related_name='group_owner')
    title=models.CharField(max_length=100)

    def __str__(self):
        return self.title






#Praiseクラス
class Praise(models.Model):
    owner=models.ForeignKey(User,on_delete=models.CASCADE,related_name='praise_owner')
    message=models.ForeignKey(Message,on_delete=models.CASCADE)

    def __str__(self):
        return 'praise for "' +str(self.message)+'"(by ' + str(self.owner) +')'

#GroupMemberクラス
class GroupMember(models.Model):
    group=models.ForeignKey(Group,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)

