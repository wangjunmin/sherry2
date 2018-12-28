import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.
# 上传并显示图片
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from pwk.utils import get_pwkQuery_set, xzbm2name, getxzcode
from .forms import QueryListForm, IndexForm, DocumentForm, ZzgccxForm
from .models import PwkInfo, ZzqkLog


@login_required(login_url='/admin/login/')
def index(request):
    form = IndexForm(request.POST or None)
    dthlChoice(request,form)
    return render(request,'pwk/index.html',{
        "form":form,
    })
@login_required(login_url='/admin/login/')
def prhlmcQuery(request):
    params = request.GET
    prhlmc=params.get("prhlmc")
    pwks= get_pwkQuery_set(request).filter(prhlmc=prhlmc).values("id", "bd_jd", "bd_wd", "psxz", "zzqk", "fspfl", "pwkmc")
    for pwk in pwks:
        pwk["psxz"]=psxzbm2name(pwk["psxz"])
        pwk["calSize"]=calSize(pwk["fspfl"])

    return render(request, 'pwk/prhlQuery.html', {
        "pwks": pwks,
    })
# 上传排污口治理过程中的图片信息
@login_required(login_url='/admin/login/')
def pwk_imglist(request):
    pwk_query(request)
    return pwk_page(request, "pwk/pwk_zlPic_list.html")
# 查看排污口信息
@login_required(login_url='/admin/login/')
def pwk_qrlist(request):
    pwk_query(request)
    return pwk_page(request,"pwk/pwk_qr.html")
# 增加分页功能
def pwk_query(request):
    form = QueryListForm(request.POST or None)
    dthlChoice(request, form)
    pwkmc = ""
    xz = ""
    zzqk = ""
    prhlmc = ""
    psqk = ""
    psxz = ""
    qrqk = ''
    if request.method == "POST" and form.is_valid():
        queryDict = form.cleaned_data
        pwkmc = queryDict["pwkmc"]
        xz = queryDict["xz"]
        zzqk = queryDict['zzqk']
        prhlmc = queryDict['prhlmc']
        psqk = queryDict['psqk']
        psxz = queryDict['psxz']
        qrqk = queryDict['qrqk']
    # 查询条件，如果都为空表示不做限制
    pwks = get_pwkQuery_set(request).all().order_by("id")
    # 查询排入河流名称
    if pwkmc:
        pwks = pwks.filter(pwkmc__icontains=pwkmc)
    if xz:
        pwks = pwks.filter(xz=xz)
    if zzqk:
        pwks = pwks.filter(zzqk=zzqk)
    if prhlmc:
        pwks = pwks.filter(prhlmc=prhlmc)

    if psqk:
        if psqk == "有排水":
            pwks = pwks.filter(fspfl__gt=0)
        else:
            pwks = pwks.filter(fspfl__lte=0)
    if psxz:
        pwks = pwks.filter(psxz=psxz)

    if not qrqk == "":
        if qrqk == "1":
            # 调整为溯源情况
            pwks = pwks.filter(syPwkbz=qrqk)
        else:
            pwks = pwks.exclude(syPwkbz='1')
    # 范围查询
    request.session["pwk_page"] = pwks
    request.session["pwk_form"] = form
@login_required(login_url='/admin/login/')
def pwk_list(request):
    pwk_query(request)
    return pwk_page(request,"pwk/pwk_list.html")
@login_required(login_url='/admin/login/')
def pwk_page(request,html="pwk/pwk_list.html"):
    # 从会话中取出分页内容
    pwk_list=request.session["pwk_page"]
    total=len(pwk_list)
    form=request.session["pwk_form"]
    paginator = Paginator(pwk_list, 7)
    page = request.GET.get('page')
    try:
        pwk_p = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        pwk_p = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        pwk_p = paginator.page(paginator.num_pages)
    # 把分页的结果返回
    return render(request, html, {
        "pwks": pwk_p,
        "total":total,
        "form": form,
    })
# 查看排污口的详细信息
@login_required(login_url='/admin/login/')
def pwk_detail(request, pwkbm):
    pwk = get_object_or_404(PwkInfo, pk=pwkbm)
    return render(request, "pwk/pwk_detail.html", {
        "pwk_detail": pwk,
    })

# 排污口详细情况
@login_required(login_url='/admin/login/')
def pwk_detail_json(request):

    pwkid = request.GET.get("pwkid")
    pwk=PwkInfo.objects.get(id=pwkid)
    if pwk:
       json=pwk.to_json()
    else:
        json="message:无此排污口"
    return HttpResponse(json, content_type='application/json')

# 地图上的查询条件
@login_required(login_url='/admin/login/')
def pwk_map_list(request):
    form = IndexForm(request.POST or None)
    dthlChoice(request, form)
    pwkmc=""
    xz=""
    zzqk=""
    prhlmc=""
    psqk=""
    if request.method == "POST" and form.is_valid():
        queryDict=form.cleaned_data
        pwkmc=queryDict["pwkmc"]
        xz=queryDict["xz"]
        zzqk=queryDict['zzqk']
        prhlmc=queryDict['prhlmc']
        psqk=queryDict['psqk']
    # 查询条件，如果都为空表示不做限制
    pwks= get_pwkQuery_set(request).all()
    # 查询排入河流名称

    if pwkmc:
        pwks=pwks.filter(pwkmc__icontains=pwkmc)
    if xz:
        pwks=pwks.filter(xz=xz)
    if zzqk:
        pwks=pwks.filter(zzqk=zzqk)
    if prhlmc:
        pwks=pwks.filter(prhlmc=prhlmc)

    if psqk:
        if psqk=="有排水":
            pwks=pwks.filter(fspfl__gt=0)
        else:
            pwks=pwks.filter(fspfl__lte=0)
    pwks = pwks.values("id", "bd_jd", "bd_wd", "zzqk", "fspfl","pwkmc")
    pwkList = []
    for pwk in pwks:
        pwk["calSize"]=calSize(pwk["fspfl"])
        pwkList.append(json.dumps(pwk,ensure_ascii = False))

    returnDict={
        "pwks":pwkList,
    }
    return JsonResponse(returnDict,safe=False)
# 排污口图形显示
@login_required(login_url='/admin/login/')
def pwk_chart(request):
    # 根据乡镇分组查询排污口数量
    xz_count= get_pwkQuery_set(request).values("xz", "zzqk").annotate(Count("id"))
    # X轴
    x=[]
    x_bm=[]
    count_xz=[]
    # 正在治理
    zzzl=[]
    # 已治理
    yzl=[]
    # 计划治理
    jhzl=[]
    # 河流已治理


    # 把所有乡镇编码取出来
    for item in xz_count:
        xzbm=item['xz']
        if xzbm in x_bm:
            pass
        else:
            x_bm.append(xzbm)
            x.append(xzbm2name(xzbm))
    # 拼装数据
    for idx,xz in enumerate(x_bm):
        for item in xz_count:
            if item['xz']==xz:
                if item['zzqk']=='已治理':
                    yzl.append(item['id__count'])
                elif item['zzqk']=='正在治理':
                    zzzl.append(item['id__count'])
                else:
                    jhzl.append(item['id__count'])
        # 没有数字的用0来填充
        if len(zzzl)!=idx+1:
            zzzl.append(0)
        if len(yzl)!=idx+1:
            yzl.append(0)
        if len(jhzl)!=idx+1:
            jhzl.append(0)
        count_xz.append(
            {
                "xz":x[idx],
                "pwks":zzzl[idx]+yzl[idx]+jhzl[idx],
                "yzl":yzl[idx],
                "jhzl":jhzl[idx],
                "zzzl":zzzl[idx]
            }
        )


    xj_count={}

    xj_count["zzzl"]=sum(zzzl)
    xj_count["yzl"]=sum(yzl)
    xj_count["jhzl"]=sum(jhzl)
    xj_count["pwk"] = xj_count["zzzl"]+xj_count["yzl"]+xj_count["jhzl"]


    # 把乡镇编码转换为名称
    return render(request,"pwk/pwk_chart.html",{
        "xAxis":x,
        "yzl":yzl,
        "zzzl":zzzl,
        "jhzl":jhzl,
        "count_xz":count_xz,
        "xj_count":xj_count,
    });

# 排水性质编码转名称

def psxzbm2name(bm):
    for dm,mc in PwkInfo.psxz_option:
        if dm==bm:
            return mc
    return '未知排水性质'

# 计算排污口的显示尺寸,显示范围为5到10
def calSize(sfpfl):
    resultSize=5

    sfpfl=sfpfl.replace("\t","").replace(" ","").replace("\n","")
    if sfpfl:
        fsfpfl=float(sfpfl)
        if fsfpfl>10 and fsfpfl<100:
            resultSize=resultSize+fsfpfl/100*5
        elif fsfpfl>=100:
            resultSize=10
    return resultSize

# 处理多个图片上传的业务
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def mutilPic(request):
    if request.method == 'POST':
        # 多个文件特别注意，
        # 要用getlist方法取数组
        files = request.FILES.getlist('docfile')
        for file in files:
            pwkbm=file.name[:-4]
            try:
                pwk=PwkInfo.objects.filter(pwkbm=pwkbm)
                if pwk.exists():
                    pwkIn=pwk[0] # 取第一个，重复的不管
                    pwkIn.pwkImage=file
                    pwkIn.save()
            except ObjectDoesNotExist:
                print("照片没有导入："+file.name)
        return HttpResponse('文件上传成功！')
    else:
        form = DocumentForm()
    return render(request, 'pwk/picUpload.html', {'form': form})



# 根据权限生成河流信息
def dthlChoice(request,form):
    hl_choice = [("","排入河流--全部")]
    hlmcs = get_pwkQuery_set(request).values("prhlmc")
    for item in hlmcs:
        newItem = (item["prhlmc"], item["prhlmc"])
        if newItem in hl_choice:
            pass
        else:
            hl_choice.append(newItem)
    form.fields['prhlmc'].choices = hl_choice
    # 处理乡镇的内容
    xzqhdm=getxzcode(request)

    if xzqhdm[0]:
        xz=[]
        xz.append(xzqhdm)
        form.fields['xz'].choices = xz

# 确认排污口信息，确认后才能进行查询统计
def qrpwk(request):
    # 增加权限，只有区县的才能确认
    userRole=getxzcode(request)

    message=""
    status=""
    if not userRole[0]:
        # 为区县用户可以修改
        id = request.GET['id']
        pwk= get_pwkQuery_set(request).get(id=id)
        if pwk.qrqk:
            pwk.qrqk=0
            status="未确认"
        else:
            pwk.qrqk=1
            status = "已确认"
        pwk.save()
        message=pwk.pwkmc+"修改成为："+status+"."

    else:
        message="只有区县用户才能操作!"
    outString = {
        "message": message,
        "status":status
    }
    return JsonResponse(outString,safe=False)

# 修改设置溯源排污口标志
def sypwk(request):
    # 增加权限，只有区县的才能确认
    userRole=getxzcode(request)

    message=""
    status=""
    if not userRole[0]:
        # 为区县用户可以修改
        id = request.GET['id']
        pwk= get_pwkQuery_set(request).get(id=id)
        if pwk.syPwkbz and pwk.syPwkbz=="是":
            pwk.syPwkbz="否"
            status="否"
        else:
            pwk.syPwkbz = "是"
            status = "是"
        pwk.save()
        message=pwk.pwkmc+"修改成为："+status+" 溯源排污口."

    else:
        message="只有区县用户才能操作!"
    outString = {
        "message": message,
        "status":status
    }
    return JsonResponse(outString,safe=False)
# 整治过程查询
def zzgcCx(request):
    form = ZzgccxForm(request.POST or None)
    dthlChoice(request, form)
    zzqks = zzqk_list_role(request)
    zzqks = zzqks.order_by("-xq_rq")
    if request.method=="POST" and form.is_valid():
        query_dict=form.cleaned_data
        pwkmc=query_dict["pwkmc"]
        xz=query_dict["xz"]
        hlmc=query_dict["prhlmc"]
        start_date=query_dict["start_date"]
        end_date=query_dict['end_date']
        if pwkmc:
            zzqks=zzqks.filter(pwkmc=pwkmc)
        if xz:
            zzqks=zzqks.filter(xz=xz)
        if hlmc:
            zzqks=zzqks.filter(hlmc=hlmc)
        if start_date:
            zzqks=zzqks.filter(xq_rq__gte=start_date)
        if end_date:
            zzqks=zzqks.filter(xq_rq__lte=end_date)
    total = zzqks.count()
    return render(request, "pwk/pwk_zzqklog.html", {"zzqk": zzqks,
                                                    "total":total,
                                                    "form":form,})

# 根据权限取整治情况
def zzqk_list_role(request):
    qs = ZzqkLog.objects
    xzdm = getxzcode(request)[0]
    if xzdm is None:
        # 返回一个空值
        qs = qs.none()
    else:
        # 乡镇用户登录
        if xzdm:
            qs = qs.filter(xz=xzdm)
    return qs
