from django.contrib.auth.models import Group
from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.utils.html import format_html
import pwk.pwkConf as conf

# Create your models here.


class PwkInfo(models.Model):
    pwkbm = models.CharField(verbose_name='排污口编码',max_length=30)
    pwkmc=models.CharField(verbose_name='排污口名称',max_length=50)
    syPwkbz=models.CharField(verbose_name="溯源排污口标志",max_length=6,choices=conf.YesNo_option,null=True,blank=True,default=None)
    # 乡镇的列表
    XZ_CHOICE =conf.XZ_CHOICE
    # 整治情况的列表
    zzqk_choice=conf.zzqk_option
    # 排水性质选项
    psxz_option = conf.psxz_option
    xz = models.CharField(verbose_name="乡镇", max_length=10, choices=XZ_CHOICE)
    # 所在村
    szc = models.CharField(verbose_name="所在村", max_length=30)
    # 排入河流名称
    prhlmc = models.CharField(verbose_name="排入河流名称", max_length=60,choices=conf.hlAll_choice)
    # 左右
    zy = models.CharField(verbose_name="左右",max_length=6,choices=conf.LeftRight_option,
                          help_text="人的朝向与河水流走的方向一致，此时以人的左右即为河的左右岸。")
    # 经度
    jd = models.FloatField(verbose_name="经度",help_text="度")
    # 维度
    wd = models.FloatField(verbose_name="纬度",help_text="度")

    bd_jd=models.FloatField(verbose_name="百度经度",null=True, blank=True, default=None)
    bd_wd=models.FloatField(verbose_name="百度维度",null=True, blank=True, default=None)

    # 排水性质
    psxz = models.CharField(verbose_name="排水性质", max_length=4,choices=psxz_option)
    # 废水排放量
    fspfl=models.CharField(verbose_name="废水排放量",max_length=8,null=True,blank=True,default=None,help_text='每天排放量，以吨为单位')
    # 是否雨污分流
    ywfl=models.CharField(verbose_name="是否雨污分流",max_length=2,choices=conf.YesNo_option,blank=True)

    # 排放规律
    pfgl=models.CharField(verbose_name="排放规律",max_length=20,null=True, blank=True, default=None,choices=conf.pfgl_choice)
    # 排污口形状
    pwkxz=models.CharField(verbose_name="入河方式", max_length=20,null=True, blank=True, default=None,choices=conf.pwkxz_choice)
    # 排污口尺寸
    # pwkcc=models.CharField(verbose_name="排污口尺寸",max_length=20,null=True, blank=True, default=None)
    # 主要排水单位
    zypsdw=models.CharField(verbose_name="上游污染源名单",max_length=800,null=True, blank=True, default=None)
    # 权属
    pwkqs=models.CharField(verbose_name="权属", max_length=200,null=True, blank=True, default=None)

    # 有无手续
    ywsx=models.CharField(verbose_name="有无手续",max_length=8,null=True,blank=True, default=None,choices=conf.yw_option)
    # 整治情况
    zzqk=models.CharField(verbose_name="整治情况",max_length=20,null=True,blank=False,default=None,choices=zzqk_choice)
    # 是否保留
    sfbl=models.CharField(verbose_name="是否保留",max_length=20,null=True,blank=True,default=None,choices=conf.YesNo_option)
    zlfs_lb=models.CharField(verbose_name="治理方式类别",max_length=40,null=True,blank=False,default=None,choices=conf.zlfs_option)
    # 治理方式
    zlfs=models.CharField(verbose_name="治理方式",max_length=200,null=True,blank=True,default=None)
    # 完成时间
    wcsj=models.DateField(verbose_name="完成时间",null=True,blank=False,default=None)

    # 责任人
    zrr=models.CharField(verbose_name="责任人",max_length=60,null=True,blank=False,default=None)
    # 监督人
    jdr=models.CharField(verbose_name="监督人",max_length=60,null=True,blank=False,default=None)
    # 工作进展
    gzjz=models.CharField(verbose_name="工作进展",max_length=200,null=True, blank=True, default=None)
    # 备注
    bz=models.CharField(verbose_name='备注',max_length=200,null=True,blank=True,default=None)
    # 确认情况
    qrqk=models.NullBooleanField(verbose_name='确认情况',null=True,default=None)
    # 排污口照片
    pwkImage = models.ImageField(verbose_name="排污口照片", upload_to='documents/%Y/%m/%d',null=True,blank=False,default=None)
    doc_thumbnail = ImageSpecField(source="pwkImage",
                                   processors=[ResizeToFill(100,50)],
                                   format="JPEG",
                                   options={"quality":60})

    def pwkThumbnail(self):
        imageUrl=""
        thumbUrl=""
        if self.pwkImage:
            imageUrl=self.pwkImage.url
            thumbUrl=self.doc_thumbnail.url
        else:
            imageUrl='#'
            thumbUrl=""

        return format_html("<div class='img-wrap' data_title='{}'> <img data_src='{}' src='{}' alt='{}'></img></div>",
                          self.pwkmc,
                          imageUrl,
                          thumbUrl,
                           "还没上传图片")

    pwkThumbnail.short_description = '排污口图片'

    # 把model转化为json字符串
    def to_json(self):
        fields=[]
        for field in self._meta.fields:
            strName=field.name
            if not(strName=="pwkImage" or strName=="doc_thumbnail"):
                fields.append(field.name)
        d={}
        for attr in fields:
            if attr=="xz":
                xzvalues=getattr(self,attr)
                for item in self.XZ_CHOICE:
                    if item[0]==xzvalues:
                        d[attr] = item[1]
                        break
            else:
                d[attr]=getattr(self,attr)
        d["pwkThumbnail"]=self.pwkThumbnail()
        d["short_psdw"]=self.short_psdw()
        import json
        return json.dumps(d)
    def __str__(self):
        return self.pwkbm

    # 处理上游污染源单位名称过长的情况
    def short_psdw(self):
        short_psdw=""
        if len(self.zypsdw)>10:
            short_psdw=self.zypsdw[:10]+"..."
        else:
            short_psdw=self.zypsdw
        return short_psdw
    # 处理治理方式过长的情况
    def short_zlfs(self):
        short_zlfs=""
        if len(self.zlfs)>10:
            short_zlfs = self.zlfs[:10] + "..."
        else:
            short_zlfs = self.zlfs
        return short_zlfs


    class Meta:
        verbose_name = "排污口"
        verbose_name_plural = verbose_name

class Xzqh(models.Model):
    name=models.CharField(verbose_name="行政区划名称",max_length=200)
    parent_name=models.CharField(verbose_name="上级代码",max_length=20)
    code=models.CharField(verbose_name="行政区划代码",max_length=20,primary_key=True)
    level=models.IntegerField(verbose_name="行政级别")

    class Meta:
        verbose_name="行政区划"
        verbose_name_plural=verbose_name
# 对排污口整治过程进行追踪，了解一段时间内各个乡镇排污口的新增、已治理、正在治理和计划治理的变化情况
class ZzqkLog(models.Model):
    pwkid=models.CharField(verbose_name="排污口ID",max_length=8,default=None)
    pwkbm = models.CharField(verbose_name='排污口编码', max_length=30)
    pwkmc = models.CharField(verbose_name='排污口名称', max_length=50)
    hlmc=models.CharField(verbose_name="河流名称",max_length=60,default=None)
    xz = models.CharField(verbose_name="乡镇", max_length=10, choices=conf.XZ_CHOICE)
    bhq_lx=models.CharField(verbose_name="变化前类型",max_length=20,null=True,blank=True,default=None)
    bhh_lx=models.CharField(verbose_name="变化后类型",max_length=20)
    xq_rq=models.DateField(verbose_name="变化日期",auto_now_add=True)
    xgr=models.CharField(verbose_name="变更人",max_length=40)

    class Meta:
        verbose_name="排污口整治日志"
        verbose_name_plural=verbose_name

# 对排污口整治进展的阶段情况提供图片证据，拍摄时间、拍摄人、描述、上传时间等
class pwkZZjz(models.Model):
    pwkid=models.CharField(verbose_name="排污口ID",max_length=8)
    pwkmc=models.CharField(verbose_name="排污口名称",max_length=60,null=True,blank=True,default=None)
    xz=models.CharField(verbose_name="乡镇",max_length=20,choices=conf.XZ_CHOICE,null=True,blank=True,default=None)
    psr=models.CharField(verbose_name="拍摄人",max_length=20)
    psDate=models.DateField(verbose_name="拍摄日期",auto_now=True,null=True)
    desc=models.TextField(verbose_name="描述",null=True,blank=True,default=None)
    # 排污口照片
    pwkImage = models.ImageField(verbose_name="排污口照片", upload_to='documents/jz/%Y/%m/%d', null=True, blank=True,
                                 default=None)
    doc_thumbnail = ImageSpecField(source="pwkImage",
                                   processors=[ResizeToFill(100, 50)],
                                   format="JPEG",
                                   options={"quality": 80})

    def pwkThumbnail(self):

        if self.pwkImage:
            imageUrl = self.pwkImage.url
            thumbUrl = self.doc_thumbnail.url
        else:
            imageUrl = '#'
            thumbUrl = ""

        return format_html("<div class='img-wrap' data_title='{}'> <img data_src='{}' src='{}' alt='{}'></img></div>",
                           self.psDate.strftime('%Y-%m-%d')+":"+self.pwkmc,
                           imageUrl,
                           thumbUrl,
                           "还没上传图片")

    pwkThumbnail.short_description = '排污口图片'
    def __str__(self):
        return self.desc
    class Meta:
        verbose_name="整治进展证据"
        verbose_name_plural=verbose_name

# 排污口修改日志
class PwkxgLog(models.Model):
    pwkid=models.CharField(verbose_name="排污口ID",max_length=10)
    pwkbm=models.CharField(verbose_name="排污口编号",max_length=30)
    pwkmc=models.CharField(verbose_name="排污口名称",max_length=60)
    xz=models.CharField(verbose_name="乡镇",max_length=60)
    xgnr=models.CharField(verbose_name="修改内容",max_length=30)
    xgnr_dm=models.CharField(verbose_name="修改内容代码",max_length=20,blank=True,default=None,null=True)
    xgq_nr=models.CharField(verbose_name="修改前内容",max_length=200,blank=True,default=None,null=True)
    xgh_nr=models.CharField(verbose_name="修改后内容",max_length=200,blank=True,default=None,null=True)
    xgr=models.CharField(verbose_name="修改人",max_length=10)
    xgsj = models.DateTimeField(verbose_name="修改时间", auto_now_add=True)
    qrxgbj=models.TextField(verbose_name="确认标志",max_length=4,blank=True,default=None,null=True)
    qrms=models.TextField(verbose_name="原因描述",max_length=100,blank=True,default=None,null=True)
    qrsj=models.DateTimeField(verbose_name="审核时间",blank=True,null=True,auto_now=True)
    pwkImage = models.ImageField(verbose_name="排污口照片", upload_to='documents/%Y/%m/%d', null=True, blank=True,
                                 default=None)


class MessageInbox(models.Model):
    sender=models.CharField(verbose_name="发送人",max_length=60)
    accepter=models.ManyToManyField(to=Group,verbose_name="接收人",related_name='m2a')
    message_text=models.TextField(verbose_name="消息正文")
    send_date=models.DateField(verbose_name="发送时间",auto_now_add=True)
    read_flag = models.BooleanField(verbose_name="阅读标志",blank=True,default=0)
    read_user = models.CharField(verbose_name="阅读人",max_length=200,blank=True)

    def to_json(self):
        d={}
        d["sender"]=self.sender
        d["message_text"]=self.message_text
        d["send_date"]=self.send_date.strftime("%Y-%m-%d")
        import json
        return json.dumps(d)

    class Meta:
        verbose_name = "公告通知"
        verbose_name_plural = verbose_name


# 排污口整治进展情况追踪
class ZzjzLog(models.Model):
    pwkId=models.CharField(verbose_name="排污口ID",max_length=10)
    pwkmc=models.CharField(verbose_name="排污口名称",max_length=60)
    zzjzID=models.CharField(verbose_name="进展图片编号",max_length=10)
    xz=models.CharField(verbose_name="乡镇",max_length=20,choices=conf.XZ_CHOICE)
    rq=models.DateField(verbose_name="上传日期",auto_now_add=True)
    scr=models.CharField(verbose_name="上传人",max_length=30)
