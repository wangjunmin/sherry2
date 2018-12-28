"""
  生成排污口整治情况报表
"""
from django.db.models import Count
from django.shortcuts import render

from pwk.pwkConf import zlfs_option,XZ_CHOICE
from pwk.utils import get_pwkQuery_set

# 排污口统计报表（各镇街排污口数量）
def pwk_tjbb(request):
    # 各乡镇总排污口数量
    xz_count=get_pwkQuery_set(request).values("xz").annotate(pwks=Count("id"))

    # 各乡镇溯源排污口数
    xz_sy_count=get_pwkQuery_set(request).filter(syPwkbz="1")\
        .values("xz").annotate(pwks=Count("id"))
    # 各乡镇新增排污口数--新增
    xz_xz_count=get_pwkQuery_set(request).exclude(syPwkbz="1")\
        .values("xz").annotate(pwks=Count("id"))
    # 各乡镇排污口治理情况
    xz_zl_count=get_pwkQuery_set(request)\
        .values("xz","zzqk").annotate(pwks=Count("id"))

    # 对已治理的排污口根据整治类别进行分类
    xz_yzl_count=get_pwkQuery_set(request).filter(zzqk="已治理")\
        .values("xz","zlfs_lb").annotate(pwks=Count("id"))
    tj_result={}
    # 开始拼装数据--总排口数量
    for item in xz_count:
        tj_result[item["xz"]]={"zpksl":item["pwks"]}
    # 溯源排污口数
    for item in xz_sy_count:
        tj_result[item["xz"]]["sypksl"] = item["pwks"]

    # 新增排污口
    for item in xz_xz_count:
        tj_result[item["xz"]]["xzpwk"] = item["pwks"]
    # 整治情况
    for item in xz_zl_count:
        if item["zzqk"]=="已治理":
            tj_result[item["xz"]]["yzl_gj"]=item["pwks"]
        if item["zzqk"]=="正在治理":
            tj_result[item["xz"]]["zzzl"] = item["pwks"]
        if item["zzqk"] == "计划治理":
            tj_result[item["xz"]]["jhzl"] = item["pwks"]
    # 已治理的排污口分类
    for item in xz_yzl_count:
        if item['zlfs_lb']=="雨水":
            tj_result[item["xz"]]["ys"]=item['pwks']
        if item['zlfs_lb']=="退水口":
            tj_result[item["xz"]]["tsk"]=item['pwks']
        if item['zlfs_lb']=="入河口":
            tj_result[item["xz"]]["rhk"]=item['pwks']
        if item['zlfs_lb']=="供水泄水口":
            tj_result[item["xz"]]["gsxsk"]=item['pwks']
        if item['zlfs_lb']=="封堵":
            tj_result[item["xz"]]["fd"]=item['pwks']
        if item['zlfs_lb']=="截污纳管":
            tj_result[item["xz"]]["jwng"]=item['pwks']
        if item['zlfs_lb']=="拆迁清除":
            tj_result[item["xz"]]["cqqc"]=item['pwks']
        if item['zlfs_lb']=="废弃":
            tj_result[item["xz"]]["fc"]=item['pwks']
        if item['zlfs_lb']=="经污水处理设施排放":
            tj_result[item["xz"]]["wscl"]=item['pwks']
        if item['zlfs_lb']=="集中收集抽运":
            tj_result[item["xz"]]["jzsjcy"]=item['pwks']
    #合计值
    hz={}
    hz["zpksl"]=get_pwkQuery_set(request).count()
    hz["sypksl"] = get_pwkQuery_set(request).filter(syPwkbz="1").count()
    hz["xz"]=get_pwkQuery_set(request).exclude(syPwkbz="1").count()
    hz["yzl_gj"] = get_pwkQuery_set(request).filter(zzqk="已治理").count()
    hz["ys"] = get_pwkQuery_set(request).filter(zzqk="已治理")\
        .filter(zlfs_lb="雨水").count()
    hz["tsk"] = get_pwkQuery_set(request).filter(zzqk="已治理") \
        .filter(zlfs_lb="退水口").count()
    hz["rhk"] = get_pwkQuery_set(request).filter(zzqk="已治理") \
        .filter(zlfs_lb="入河口").count()
    hz["gsxsk"] = get_pwkQuery_set(request).filter(zzqk="已治理") \
        .filter(zlfs_lb="供水泄水口").count()
    hz["fd"] = get_pwkQuery_set(request).filter(zzqk="已治理") \
        .filter(zlfs_lb="封堵").count()
    hz["jwng"] = get_pwkQuery_set(request).filter(zzqk="已治理") \
        .filter(zlfs_lb="截污纳管").count()
    hz["cqqc"] = get_pwkQuery_set(request).filter(zzqk="已治理") \
        .filter(zlfs_lb="拆迁清除").count()
    hz["fc"] = get_pwkQuery_set(request).filter(zzqk="已治理") \
        .filter(zlfs_lb="废弃").count()
    hz["wscl"] = get_pwkQuery_set(request).filter(zzqk="已治理") \
        .filter(zlfs_lb="经污水处理设施排放").count()
    hz["jzsjcy"] = get_pwkQuery_set(request).filter(zzqk="已治理") \
        .filter(zlfs_lb="集中收集抽运").count()
    hz["zzzl"]=get_pwkQuery_set(request).filter(zzqk="正在治理").count()
    hz["jhzl"] = get_pwkQuery_set(request).filter(zzqk="计划治理").count()
    # 乡镇
    xz={}
    for item in XZ_CHOICE:
        xz[item[0]]=item[1]

    for k,item in tj_result.items():
        item["xzmc"]=xz[k]
    return render(request,"pwk/pwk_tjbb.html",{
        "result":tj_result,
        "xz":xz,
        "hz":hz
    })