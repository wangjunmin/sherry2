# 排污口的治理证据管理
import json

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.
# 上传并显示图片
from django.db.models import Count,Sum
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from pwk.utils import xzChoice
from .models import PwkInfo, pwkZZjz, ZzjzLog
from .forms import QueryListForm, IndexForm, DocumentForm, ZzgccxForm, ZzjzForm


@login_required(login_url='/admin/login/')
def zlzjInput(request):
    pwkid = request.GET.get("pwkid")
    if request.method == "GET":
        pwk = PwkInfo.objects.get(id=pwkid)
        if not pwk:
            raise ObjectDoesNotExist
        form = ZzjzForm(initial={'pwkid':pwkid,"pwkmc":pwk.pwkmc})
        return render(request, "pwk/pwk_pwkzlzj.html", {'form': form})
    elif request.method == "POST":
        form = ZzjzForm(request.POST or None)
        post_dict=request.POST
        pwkid=post_dict.get("pwkid")
        pwk=PwkInfo.objects.get(id=pwkid)
        pwkmc=pwk.pwkmc
        xz=pwk.xz
        psr=post_dict.get("psr")
        desc=post_dict.get("desc")
        zzjz=pwkZZjz()
        zzjz.pwkid=pwkid
        zzjz.pwkmc=pwkmc
        zzjz.xz=xz
        zzjz.psr=psr
        zzjz.desc=desc
        zzjz.pwkImage=request.FILES.get("pwkImage")
        zzjz.save()
        zzlog = ZzjzLog()
        zzlog.pwkId = pwk.id
        zzlog.pwkmc = pwk.pwkmc
        zzlog.zzjzID = zzjz.id
        zzlog.xz = pwk.xz
        zzlog.scr = request.user.username
        zzlog.save()
        return render(request, "pwk/pwk_pwkzlzj.html",
                      {'form': form,'message':'保存成功'})
    else:
        print(request.method)
# 查询每个排污口的治理情况的描述
@login_required(login_url='/admin/login/')
def zlzjQuery(request):
    pwkid=request.GET.get("pwkid")
    pwkmc=""
    if pwkid:
        pwkmc=PwkInfo.objects.get(id=pwkid).pwkmc
        zlzjs=pwkZZjz.objects.filter(pwkid=pwkid).order_by("-id")
        return render(request, "pwk/pwk_zlzjList.html",
                          {'zlzjs': zlzjs,
                           'pwkmc':pwkmc,})
    else:
        return HttpResponseRedirect('/pwk/index')
