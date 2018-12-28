from django.conf.urls import url

from pwk import XzModifyView, MessageView
from pwk.gviews import IndexView, QureyPwkView
from . import views
from . import ZlzjPic
from . import BbView

urlpatterns = [
    # 一张图
    url(r"^index/", views.index, name="index"),
    # 排污口查询
    url(r"^pwk_list/", QureyPwkView.as_view(), name="pwk_list"),
    # 地图上展示排污口简要数据
    url(r"^pwk_detail_json/",views.pwk_detail_json, name="pwk_json"),
    # 排污口详细数据
    url(r'^(?P<pwkbm>[0-9]*)/$', views.pwk_detail, name="pwk_detail"),
    # 排污口统计图
    url(r'^pwk_chart/',views.pwk_chart,name="pwk_chart"),
    # 排污口查询分页
    url(r'^pwk_page/',views.pwk_page,name='pwk_page'),
    # 地图上条件查询
    url(r'^pwk_map_list/',views.pwk_map_list,name='pwk_map_list'),
    # 根据河流名称查询
    url(r'^pwk_hlmc/',views.prhlmcQuery,name='prhlmc'),
    # 图片批量上传
    url(r'^pwk_picUpload/', views.mutilPic, name='picUpload'),
    # 排污口锁定
    url(r'^pwk_qrpwk/',views.qrpwk,name='qrqk'),
    # 设定排污口是否为溯源排污口
    url(r'^pwk_sypwk/',views.sypwk,name='syqk'),
    # 管理排污口的查询页
    url(r'^pwk_glpwk/',views.pwk_qrlist,name='glqk'),
    # 整治结果情况查询
    url(r"^zzqklog/",views.zzgcCx,name='zzqklog'),
    # 治理过程录入
    url(r"^zlzjlr/",ZlzjPic.zlzjInput,name='zlzj'),
    # 治理过程详情查看查询
    url(r"^zlzjList/",ZlzjPic.zlzjQuery,name='zlzjQuery'),
    # 查询定位需要录入或查看治理过程的排污口
    url(r"^zlimg/",views.pwk_imglist,name='zlimg'),
    # 排污口报告生成
    url(r"^bbtj/",BbView.pwk_tjbb,name='tjbb'),
    # 查看修改日志
    url(r"^xglog/",XzModifyView.modifyQuery,name='xglog'),
    # 查看公告通知详情
    url(r"^readMessage/",MessageView.readMessage,name='readMessage'),
    # 查看未读公告通知
    url(r"^unreadMessage/", MessageView.unreadMessageV, name='unreadMessage'),
    # 查看所有公告通知
    url(r"^allMessage/", MessageView.allMessageV, name='allMessage'),
    # 修改日志详细查询
    url(r"^xglogDetail/",XzModifyView.detailLog,name="detailLog"),
    # 修改日志确认
    url(r"^qrModify/",XzModifyView.qrModify,name="qrModify"),
    # 查看上传照片的记录
    url(r"^zzjzLogQuery/", XzModifyView.zzjzLogQuery, name="zzjzLogQuery"),
    # 取未读的消息数量
    url(r"^unreadcount/", MessageView.getUnreadMessage, name="unread_count"),
]