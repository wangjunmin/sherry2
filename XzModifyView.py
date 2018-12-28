# 乡镇对排污口的修改情况进行追踪
# 查询修改情况，要考虑数据量可能有点大的问题
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import render

from pwk.forms import ModifyQueryForm
from pwk.models import PwkxgLog, PwkInfo, ZzqkLog, ZzjzLog, MessageInbox
from pwk.utils import getxzcode, xzcode2name, xzChoice
import requests
import json

@login_required(login_url='/admin/login/')
def modifyQuery(request):
    page = request.GET.get('page')
    form = ModifyQueryForm(request.POST or None)
    xzChoice(request, form)
    xgLog = xgqk_list_role(request)
    if request.method == "POST" and form.is_valid():
        query_dict = form.cleaned_data
        pwkmc = query_dict["pwkmc"]
        xz = query_dict["xz"]
        start_date = query_dict["start_date"]
        end_date = query_dict['end_date']
        if pwkmc:
            xgLog = xgLog.filter(pwkmc=pwkmc)
        if xz:
            xgLog = xgLog.filter(xz=xzcode2name(xz))
        if start_date:
            xgLog = xgLog.filter(xgsj__gte=start_date)
        if end_date:
            xgLog = xgLog.filter(xgsj__lte=end_date)
        request.session["xgLog"] = xgLog
        request.session["xgForm"] = form
    else:
        if not request.session.get("xgLog") or not page:
            request.session["xgLog"]=xgLog
            request.session["xgForm"] = form
    # 处理分页

    xglist = request.session["xgLog"]
    total = len(xglist)
    form = request.session["xgForm"]
    paginator = Paginator(xglist, 10)

    try:
        xglist_p = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        xglist_p = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        xglist_p = paginator.page(paginator.num_pages)
    # 把分页的结果返回

    xzcode = getxzcode(request)
    if xzcode[0]:
        xz="1"
    else:
        xz="0"
    return render(request, "pwk/xgLog.html", {
        "xglist": xglist_p,
        "total": total,
        "form": form,
        "xz":xz,
    })
# 确认修改，只能区县用户确认
# 确认后，完成修改入库
# 拒绝，说明原因
@login_required(login_url='/admin/login/')
def qrModify(request):
    xzdm = getxzcode(request)[0]
    message=""
    qrqk=""
    qrms=""
    id=""
    if xzdm:
        message="只有区县用户才能确认修改信息！"
    else:
        xgLogId=request.GET.get("id")
        id=xgLogId
        qrqk=request.GET.get("qrqk")
        qr_message=request.GET.get("message")
        qrms=qr_message
        if xgLogId:
            xgLog = xgqk_list_role(request)
            xgLog=xgLog.filter(id=xgLogId)
            if xgLog:
                xglog=xgLog[0]
                xglog.qrxgbj=qrqk
                xglog.qrms=qr_message
                xglog.save()
                if qrqk == "1":
                    savePwk(xglog)
                    sendMessage(request, xglog, "接受")
                else:
                    pwk=PwkInfo.objects.get(id=xglog.pwkid)
                    print(pwk)
                    if pwk:
                        pwk.qrqk=False
                        pwk.save()
                    sendMessage(request, xglog, "拒绝")
                message="确认修改成功！"
            else:
                message="无此记录"
        else:
            message="无此修改记录"
    ret={"message":message,
         "qrqk":qrqk,
         "qrms":qrms,
         "id":id
        }
    return JsonResponse(ret,safe=True)

def savePwk(xglog):
    pwkid=xglog.pwkid
    pwk=PwkInfo.objects.get(id=pwkid)
    if xglog.xgnr_dm=="addNew":
        pwk.qrqk=True
        pwk.save()
        # 记录整治状态的调整
        doLog(pwk, xglog.xgh_nr, False, xglog.xgr)
    else:
        if xglog.xgnr_dm=="jd":
            jd=xglog.xgh_nr
            wd=pwk.wd
            transBD(jd,wd,pwk)
        if xglog.xgnr_dm=="wd":
            wd = xglog.xgh_nr
            jd = pwk.jd
            transBD(jd, wd, pwk)
        if xglog.xgnr_dm=="zzqk":
            doLog(pwk,xglog.xgh_nr,True,xglog.xgr)
        if xglog.xgnr_dm=="pwkImage":
            pwk.pwkImage=xglog.pwkImage
        else:
            setattr(pwk, xglog.xgnr_dm, xglog.xgh_nr)
        pwk.save()
# 根据权限取修改情况
def xgqk_list_role(request):
    qs = PwkxgLog.objects.order_by("-xgsj")
    xzdm = getxzcode(request)[0]
    xzmc = getxzcode(request)[1]
    if xzdm is None:
        # 返回一个空值
        qs = qs.none()
    else:
        # 乡镇用户登录
        if xzdm:
            qs = qs.filter(xz=xzmc)
    return qs
# 坐标自动转换为baidu坐标
def transBD(jd,wd,pwk):
    BDSERVICE = "http://api.map.baidu.com/geoconv/v1/?coords=%s,%s&from=1&to=5&ak=v2k8lLfAPWz4Qbzy3GedU0TBYTGbhiGc"
    urlAPI = BDSERVICE % (jd, wd)
    req = requests.get(urlAPI, timeout=2)
    content = req.content
    oResult = json.loads(content.decode())
    x = oResult["result"][0]["x"]
    y = oResult["result"][0]["y"]
    pwk.bd_jd = x
    pwk.bd_wd = y

# 记录整治状态
def doLog(obj,bhh,change,xgr):
    pwkbm=obj.pwkbm
    pwkmc=obj.pwkmc
    xz=obj.xz
    hlmc=obj.prhlmc
    pwkid=obj.id
    bhq_lx=""
    if change:
        bhq_lx=obj.zzqk
        bhh_lx=bhh
    else:
        # 新增
        bhh_lx="新增"
    if not bhq_lx==bhh_lx:
        zzqk=ZzqkLog()
        zzqk.pwkid=pwkid
        zzqk.pwkbm=pwkbm
        zzqk.pwkmc=pwkmc
        zzqk.xz=xz
        zzqk.hlmc=hlmc
        zzqk.bhq_lx=bhq_lx
        zzqk.bhh_lx=bhh_lx
        zzqk.xgr=xgr
        zzqk.save()
# 取修改日志的详细信息
def detailLog(request):
    xgLogId = request.GET.get("logid")
    xglog=PwkxgLog.objects.get(id=xgLogId)
    xglogDict={
        "id":xglog.id,
        "pwkmc":xglog.pwkmc,
        "xgnr":xglog.xgnr,
        "xgq_nr":xglog.xgq_nr,
        "xgh_nr":xglog.xgh_nr
    }
    return JsonResponse(xglogDict)


# 整治进展提交证据查询
@login_required(login_url='/admin/login/')
def zzjzLogQuery(request):
    page = request.GET.get('page')
    form = ModifyQueryForm(request.POST or None)
    xzChoice(request, form)
    xgLog = zzjz_list_role(request)
    if request.method == "POST" and form.is_valid():
        query_dict = form.cleaned_data
        pwkmc = query_dict["pwkmc"]
        xz = query_dict["xz"]
        start_date = query_dict["start_date"]
        end_date = query_dict['end_date']
        if pwkmc:
            xgLog = xgLog.filter(pwkmc=pwkmc)
        if xz:
            xgLog = xgLog.filter(xz=xz)
        if start_date:
            xgLog = xgLog.filter(rq__gte=start_date)
        if end_date:
            xgLog = xgLog.filter(rq__lte=end_date)
        request.session["zzjzLog"] = xgLog
        request.session["zzjzForm"] = form
    else:
        if not request.session.get("zzjzLog") or not page:
            request.session["zzjzLog"]=xgLog
            request.session["zzjzForm"] = form
    # 处理分页

    xglist = request.session["zzjzLog"]
    total = len(xglist)
    form = request.session["zzjzForm"]
    paginator = Paginator(xglist, 10)

    try:
        xglist_p = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        xglist_p = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        xglist_p = paginator.page(paginator.num_pages)
    # 把分页的结果返回
    return render(request, "pwk/zzjzLog.html", {
        "xglist": xglist_p,
        "total": total,
        "form": form,
    })



def zzjz_list_role(request):
    qs = ZzjzLog.objects.order_by("-rq")
    xzdm = getxzcode(request)[0]
    xzmc = getxzcode(request)[1]
    if xzdm is None:
        # 返回一个空值
        qs = qs.none()
    else:
        # 乡镇用户登录
        if xzdm:
            qs = qs.filter(xz=xzdm)
    return qs
# 给乡镇发公告通知，告知排污口已经被修改
def sendMessage(request,logobject,qrjg):
    mbox=MessageInbox()
    mbox.sender=request.user.username
    pwk=PwkInfo.objects.get(id=logobject.pwkid)
    xzname=xzcode2name(pwk.xz)
    message='对"%s"的"%s"调整被%s%s' % (logobject.pwkmc,logobject.xgnr,request.user.get_short_name(),qrjg)
    mbox.message_text=message
    mbox.save()
    g,dummy = Group.objects.get_or_create(name=xzname)
    mbox.accepter.add(g)