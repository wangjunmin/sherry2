# 处理消息
# 获取没有阅读的消息
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from pwk.models import MessageInbox

# 取所有能够阅读的消息
from pwk.utils import getxzcode

@login_required(login_url='/admin/login/')
def readableMessage(request):

    group = request.user.groups.all()[0]
    messageIn=group.m2a.all().order_by("-send_date")
    username=request.user.username
    for item in messageIn:
        if item.read_user.find(username)==-1:
            # 未读
            item.read_flag=0
        else:
            item.read_flag=1
    return messageIn

# 查看所有的公告通知

def unreadMessageV(request):
    mList=readableMessage(request)
    xzcode=getxzcode(request)
    if xzcode[0]:
        xz="1"
    else:
        xz="0"
    return render(request, "pwk/messageInbox.html", {
        "messageList": mList,
        "xz":xz
    })
# 查看我发送的公告通知
def allMessageV(request):
    userName = request.user.username
    mList=MessageInbox.objects.filter(sender=userName).order_by("-send_date")
    resultJson=[]
    for item in mList:
        resultJson.append(item.to_json())
    result={
        "messages":resultJson
    }
    return JsonResponse(result, safe=False)
# 阅读消息
def readMessage(request):
    userName = request.user.username
    messageID=request.GET.get("id")
    m_str=""
    message=""
    if messageID:
        m=MessageInbox.objects.get(id=messageID)
        print(m)
        if m:
            reader=m.read_user
            # 如果以前没有读过
            if reader.find(userName) == -1:
                reader=reader + ","+userName
                m.read_user=reader
                m.save()
            m_str=m.to_json()
        else:
            message="消息不存在！"
    else:
        message="消息不存在!"
    returnMsg= {
        "message":message,
        "mail":m_str
    }
    return JsonResponse(returnMsg, safe=True)
# 用ajax 取未读消息数量
def getUnreadMessage(request):
    lists = readableMessage(request)
    count = 0
    for item in lists:
        if item.read_flag==0:
            count += 1

    result = {
        "unread": count
    }
    return JsonResponse(result, safe=False)



