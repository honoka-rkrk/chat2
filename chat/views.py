from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import messages

from .models import Message,Group,Praise,GroupMember
from .forms import GroupCheckForm,GroupSelectForm,SearchForm,OtherUserForm,CreateGroupForm,PostForm

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

#indexのビュー関数
@login_required(login_url='/admin/login/')
def index(request):
    #publicのユーザーを取得
    (public_user,public_group)=get_public()

    #POST送信時の処理
    if request.method == 'POST':
        #Groupsのチェックを更新した時の処理
        if request.POST['mode'] == '__check_form__':
            #フォームの用意
            searchform=SearchForm()
            checkform=GroupCheckForm(request.user,request.POST)
            #チェックされたGroup名をリストにまとめる?
            glist=[]
            for item in request.POST.getlist('groups'):
                glist.append(item)
            #Messageの取得
            messages = get_your_group_message(request.user,glist,None)
        
        #Groupsメニューを変更した時の処理
        if request.POST['mode'] == '__search_form__':
            #フォームの用意
            searchform=SearchForm(request.POST)
            checkform=GroupCheckForm(request.user)
            #Groupのリストを取得
            gps=GroupMember.objects.filter(user=request.user)
            glist=[public_group]
            for item in gps:
                glist.append(item)
            #メッセージを取得
            messages=get_your_group_message(request.user,glist,request.POST['search'])
    #GETアクセス時の処理
    else:
        #フォームの用意
        searchform=SearchForm()
        checkform=GroupCheckForm(request.user)
        #Groupのリストを取得
        gps=GroupMember.objects.filter(user=request.user)
        glist=[public_group]
        for item in gps:
            glist.append(item)
        #メッセージの取得
        messages=get_your_group_message(request.user,glist,None)
    
    #共通処理
    params={
        'login_user':request.user,
        'contents':messages,
        'check_form':checkform,
        'search_form':searchform,
        }
    return render(request, 'chat/index.html',params)

@login_required(login_url='/admin/login/')
def groups(request):
    #Publicを取得
    # (public_user,public_group)=get_public()
    all_user = User.objects.all()

    #POST送信時の処理
    if request.method == 'POST':

        #Groupメニュー選択肢の処理
        if request.POST['mode'] == '__groups_form__':
            #選択肢たGroup名を取得
            sel_group=request.POST['groups']
            #Groupを取得
            gp=Group.objects.filter(owner=request.user).filter(title=sel_group).first()
            #Groupに入っているMemberを取得
            ms=GroupMember.objects.filter(group=gp)
            #GroupのMemberのUserをリストにまとめる
            vlist=[]
            for item in ms:
                vlist.append(item.user.username)
            #フォームの用意
            groupsform=GroupSelectForm(request.user,request.POST)
            otheruserform=OtherUserForm(request.user)
        
        #Memberを新しく追加
        if request.POST['mode'] == '__otheruser_form__':
            #選択したGroupの取得
            sel_group=request.POST['group']
            group_obj=Group.objects.filter(title=sel_group).first()
            #チェックした人を取得
            sel_pub=request.POST['all_user']
            #チェックした人のUserを取得
            sel_users=User.objects.filter(username=sel_pub).first()
            #Userのリストに含まれるユーザーが登録したGroupMembarを取得
            #gm=GroupMember.objects.filter(user__in=sel_users)
            #全てのMembersにGroupを設定し保存する
            gm=GroupMember()
            gm.user=sel_users
            gm.group=group_obj
            gm.save()
            #メッセージを設定
            messages.success(request,'チェックされたUserを' + \
            sel_group + 'に登録しました。')
            #フォームの用意
            groupsform=GroupSelectForm(request.user, \
                {'groups':sel_group})
            otheruserform=OtherUserForm(request.user)
    #GETアクセス時の処理
    else:
        #フォームの用意
        groupsform=GroupSelectForm(request.user)
        otheruserform=OtherUserForm(request.user)
        sel_group = '-'
    
    #共通処理
    createform=CreateGroupForm()
    params={
        'login_user':request.user,
        'groups_form':groupsform,
        'otheruser_form':otheruserform,
        'create_form':createform,
        'group':sel_group,
        }
    return render(request,'chat/groups.html',params)

#グループの作成処理
@login_required(login_url='/admin/login/')
def creategroup(request):
    #Groupを作り、Userとtitleを設定して保存する
    gp=Group()
    gp.owner=request.user
    gp.title=request.POST['group_name']
    gp.save()
    
    gm=GroupMember()
    gm.user=request.user
    gm.group=Group.objects.filter(title=gp.title).first()
    gm.save()
    messages.info(request,'新しいグループを作成しました。')
    return redirect(to='/chat/groups')

#メッセージのポスト処理
@login_required(login_url='/admin/login/')
def post(request):
    #POST送信の処理
    if request.method == 'POST':
        #送信内容の取得
        gr_name=request.POST['groups']
        content=request.POST['content']
        #Groupの取得
        group=Group.objects.filter(title=gr_name).first()
        if group == None:
            (pub_user,group)=get_public()
        #Messageを作成し設定して保存
        msg=Message()
        msg.owner=request.user
        msg.group=group
        msg.content=content
        msg.save()
        #メッセージを設定
        messages.success(request,'新しいメッセージを投稿しました！')
        return redirect(to='/chat')
    
    #GETアクセス時の処理
    else:
        form=PostForm(request.user)
    
    #共通処理
    params={
        'login_user':request.user,
        'form':form,
    }
    return render(request,'chat/post.html',params)

#Praiseボタンの処理
@login_required(login_url='/admin/login/')
def praise(request,praise_id):
    #praiseするMessageを取得
    praise_msg=Message.objects.get(id=praise_id)
    #自分がメッセージにpraiseした数を調べる
    is_praise=Praise.objects.filter(owner=request.user) \
        .filter(message=praise_msg).count()
    #ゼロより大きければ既にpraise済み
    if is_praise > 0:
        messages.success(request,'既にメッセージはPraiseしています。')
        return redirect(to='/chat')

    #Messageのpraise_countを１増やす
    praise_msg.praise_count += 1
    praise_msg.save()
    #Praiseを作成し、設定して保存
    praise=Praise()
    praise.owner=request.user
    praise.message=praise_msg
    praise.save()
    #メッセージを設定
    messages.success(request,'メッセージをPraiseしました！')
    return redirect(to='/chat')

#これ以降はビュー関数ではなく普通の関数

#指定されたグループおよび検索文字によるMessageの取得
def get_your_group_message(owner,glist,find):
    groups = Group.objects.filter(title__in=glist)
    #Groupに含まれるMemberの取得
    gp_members=GroupMember.objects.filter(group__in=groups)
    #自分が作ったグループの取得
    mygroups=GroupMember.objects.filter(user=owner)
    #自分が作ったグループをリストにまとめる
    my_groups=[]
    for mm in mygroups:
        my_groups.append(mm.group)
    #groupがgroupsに含まれるか、me_groupsに含まれるMessageの取得
    if find==None:
        messages = Message.objects.filter(group__in=groups)[:100]
    else:
        messages = Message.objects.filter(group__in=my_groups).filter(content__contains=find)[:100]
    return messages

#publicなUserとGroupを取得する
def get_public():
    public_user = User.objects.filter(username='public').first()
    public_group=Group.objects.filter \
        (owner=public_user).first()
    return (public_user,public_group)

# def get_all():
#     all_user = User.objects.all()
#     return all_user






