from django.contrib import admin
from django.shortcuts import redirect

from pwk.forms import PwkInfoForm
from pwk.models import PwkInfo, pwkZZjz, PwkxgLog, MessageInbox, ZzjzLog
from pwk.utils import getxzcode, jwtrans


class PwkAdmin(admin.ModelAdmin):
    actions = None
    list_display = ('pwkbm', 'pwkmc','xz','szc', 'prhlmc', 'zy', 'zzqk', 'pwkThumbnail')
    readonly_fields = ('pwkThumbnail',)
    exclude=("bd_jd","bd_wd",'qrqk',"syPwkbz",)
    search_fields = ['pwkbm','pwkmc']
    list_editable = ['zzqk']
    list_per_page = 10
    fieldsets = [
        ('排污口基本信息', {'fields': ['pwkbm', 'pwkmc', 'xz', 'szc',
                                'prhlmc', 'zy', 'jd', 'wd', ]}),
        ('排污信息', {'fields': ['psxz', 'fspfl', 'ywfl',
                             'pfgl', 'pwkxz', 'zypsdw', 'pwkqs']}),
        ('整治情况', {'fields': ['ywsx', 'zzqk', 'sfbl', 'zlfs_lb',
                             'zlfs', 'wcsj', 'zrr', 'jdr', 'gzjz', 'bz', 'pwkImage']}),
    ]
    form = PwkInfoForm
    list_filter = ("xz",)
    list_per_page=10

    # 增加管理站点的权限控制，乡镇的只能看乡镇的数据
    # 根据用户的组来限制
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 不考虑拒绝的数据
        qs=qs.exclude(qrqk='0')
        # 取用户所在的组，只能一个组，多余的组不考虑。
        groups=request.user.groups.values_list('name', flat=True)
        if not groups:
            # 返回一个空值
            qs=qs.none()
        else:
            groupname=groups[0]
            #暂时不考虑名称重复的情况
            xzqhdm=''
            for item in PwkInfo.XZ_CHOICE:
                if groupname==item[1]:
                    xzqhdm=item[0]
                    break
            # 乡镇用户登录
            if xzqhdm:
                qs=qs.filter(xz=xzqhdm)
        return qs

    # 保存时只是记日志，具体的保存动作要在确认的时候进行
    def save_model(self, request, obj, form, change):
        if not change or not obj.qrqk:
            super(PwkAdmin, self).save_model(request, obj, form, change)
            changed_data = form.changed_data
            i = changed_data.count('jd') + changed_data.count('wd')
            if i > 0:  # 经纬度有改变
                bdjd, bdwd = jwtrans(obj.jd, obj.wd)
                obj.bd_jd = bdjd
                obj.bd_wd = bdwd
                obj.save()
            if not change:
                self._add_audit(obj=obj, request=request)
        else:  # 修改，记录日志信息，需要确认
            self._change_audit(obj=obj, form=form, request=request)

    def _add_audit(self, request, obj):
        pwklog = PwkxgLog()
        pwklog.pwk = obj
        pwklog.xgnr_dm = "addNew"
        pwklog.xgnr = "新增"
        pwklog.xgr = request.user.username
        pwklog.save()

    def _change_audit(self, obj, form, request):
        old_pwk = PwkInfo.objects.get(id=obj.id)
        changed_data = form.changed_data
        for k in changed_data:
            pwklog = PwkxgLog()
            pwklog.pwkid = obj.id
            pwklog.pwkbm = obj.pwkbm
            pwklog.pwkmc = obj.pwkmc
            pwklog.xz = request.user.groups.values_list('name', flat=True)[0]
            pwklog.xgnr = obj._meta.get_field(k).verbose_name.title()
            pwklog.xgnr_dm = k
            pwklog.xgq_nr = getattr(old_pwk, k, "没取到")
            pwklog.xgh_nr = getattr(obj, k, "没取到")
            pwklog.xgr = request.user.username
            if k == "pwkImage":
                img = request.FILES.get('pwkImage')
                if img:
                    pwklog.pwkImage = img
            pwklog.save()

    # 动态修改乡镇和河流的选择项
    def formfield_for_choice_field(self, db_field, request, **kwargs):
        xz=getxzcode(request)
        if db_field.name == "xz":
            if xz[0]:
                # 乡镇用户
                kwargs['choices'] =(xz,)
        if db_field.name == "prhlmc":
            if xz[0]:
                # 乡镇用户
                hls=PwkInfo.objects.filter(xz=xz[0]).values("prhlmc").distinct()
                hlList=[]
                for item in hls:
                    hlList.append((item["prhlmc"],item["prhlmc"],))
                kwargs['choices']=hlList
        return super(PwkAdmin, self).formfield_for_choice_field(db_field, request, **kwargs)

    # 在详细页面不出现删除按钮
    def has_delete_permission(self, request, obj=None):
        return False


# 排污口的整治证据
class ZzzjAdmin(admin.ModelAdmin):
    actions = None
    list_per_page = 10
    def log_addition(self, request, object):
        zzlog=ZzjzLog()
        zzlog.pwkd=object.pwkid
        pwk=PwkInfo.objects.get(id=object.pwkid)
        zzlog.pwkmc=pwk.pwkmc
        zzlog.zzjzID=object.id
        zzlog.xz=pwk.xz
        zzlog.scr=request.user.username
        zzlog.save()

# 发送消息
class MessageInboxAdmin(admin.ModelAdmin):
    list_display = ('message_text', 'send_date')
    search_fields = ['sender', 'message_text']
    list_per_page = 10
    exclude = ('sender','send_date','read_flag','read_user')
    filter_horizontal = ('accepter',)
    def save_model(self, request, obj, form, change):
        if not change:
            obj.sender=request.user.username
        super(MessageInboxAdmin, self).save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        return redirect("/pwk/unreadMessage")
admin.site.site_header = '昌平区入河排污口电子地图系统'
admin.site.site_title = '排污口电子地图'
admin.site.site_url= '/pwk/index/'
admin.site.disable_action('delete_selected')
admin.site.register(PwkInfo, PwkAdmin)
admin.site.register(pwkZZjz,ZzzjAdmin)
admin.site.register(MessageInbox,MessageInboxAdmin)