from django import forms
from.models import Message,Group,Praise,GroupMember
from django.contrib.auth.models import User

#メッセージのフォーム
class MessageForm(forms.ModelForm):
    class Meta:
        model=Message
        fields=['owner','group','content']

#グループのフォーム
class GroupForm(forms.ModelForm):
    class Meta:
        model=Group
        fields=['owner','title']

#Memberのフォーム
class GroupMemberForm(forms.ModelForm):
    class Meta:
        model=GroupMember
        fields=['user','group']

#Praiseのフォーム
class PraiseForm(forms.ModelForm):
    class Meta:
        model=Praise
        fields=['owner','message']

#検索フォーム
class SearchForm(forms.Form):
    search=forms.CharField(max_length=100)

#グループのチェックボックスフォーム
class GroupCheckForm(forms.Form):
    def __init__(self,user, *args, **kwargs):
        super(GroupCheckForm,self).__init__(*args,**kwargs)
        self.fields['groups']=forms.MultipleChoiceField(
            choices=[(item.group,item.group) for item in \
            GroupMember.objects.filter(user=user)],
            widget=forms.CheckboxSelectMultiple(),
        )

#グループの選択メニューフォーム
class GroupSelectForm(forms.Form):
    def __init__(self,user,*args,**kwargs):
        super(GroupSelectForm,self).__init__(*args,**kwargs)
        self.fields['groups']=forms.ChoiceField(
            choices=[('-','-')]+[(item.title,item.title) \
                for item in Group.objects.filter(owner=user)],
        )

#Publicのチェックボックスフォーム
class OtherUserForm(forms.Form):
    def __init__(self,user,*args,**kwargs):
        super(OtherUserForm,self).__init__(*args,*kwargs)
        all_user = User.objects.all()
        self.fields['all_user']=forms.ChoiceField(
            choices=[(item.username,item.username) for item in all_user],
            #widget=forms.Select(),       
        )

#グループ作成フォーム
class CreateGroupForm(forms.Form):
    group_name=forms.CharField(max_length=50)

#投稿フォーム
class PostForm(forms.Form):
    content=forms.CharField(max_length=500, \
        widget=forms.Textarea)
    
    def __init__(self,user,*args,**kwargs):
        super(PostForm,self).__init__(*args,**kwargs)
        public=User.objects.filter(username='public').first()
        self.fields['groups']=forms.ChoiceField(
            choices=[('-','-')]+[(item.group,item.group) \
                for item in GroupMember.objects.filter(user__in=[user,public])],
        )

