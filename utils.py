
# 取乡镇代码，用名值对的形式返回
import json

from django.contrib.sites import requests

from pwk.models import PwkInfo
from pwk.pwkConf import XZ_CHOICE


def getxzcode(request):
    groups = request.user.groups.values_list('name', flat=True)
    if not groups:
        return (None,None)
    groupname = groups[0]
    xzqhdm = ''
    for item in XZ_CHOICE:
        if groupname == item[1]:
            xzqhdm = item[0]
            break
    return (xzqhdm,groupname)

# 根据权限取排污口数据
def get_pwkQuery_set(request):
    qs = PwkInfo.objects
    # 只有确认的排污口才能算
    qs = qs.filter(qrqk=1)
    xzdm=getxzcode(request)[0]
    if xzdm is None:
        # 返回一个空值
        qs = qs.none()
    else:
        # 乡镇用户登录
        if xzdm:
            qs = qs.filter(xz=xzdm)
    return qs


def xzbm2name(bm):
    for dm,mc in XZ_CHOICE:
        if dm==bm:
            mc=mc.rstrip("街道")
            mc=mc.rstrip("镇")
            mc=mc.rstrip("地区")
            return mc
    return "未知乡镇"+bm
# 根据乡镇编码取名称，完整的名称
def xzcode2name(code):
    for dm,mc in XZ_CHOICE:
        if dm==code:
            return mc
    return "未知乡镇"+code

# 根据权限生成乡镇信息
def xzChoice(request,form):
    xzqhdm = getxzcode(request)
    if xzqhdm[0]:
        xz = []
        xz.append(xzqhdm)
        form.fields['xz'].choices = xz

# 经纬度的转换
def jwtrans(jd, wd):
    BDSERVICE = "http://api.map.baidu.com/geoconv/v1/?coords=%s,%s&from=1&to=5&ak=v2k8lLfAPWz4Qbzy3GedU0TBYTGbhiGc"
    urlAPI = BDSERVICE % (jd, wd)
    req = requests.get(urlAPI, timeout=2)
    content = req.content
    oResult = json.loads(content.decode())
    bdjd = oResult["result"][0]["x"]
    bdwd = oResult["result"][0]["y"]
    return bdjd, bdwd
