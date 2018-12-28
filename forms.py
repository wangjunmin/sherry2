from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML
from django.forms import ModelForm

import pwk.pwkConf as conf
# 多个图片上传的表单
from pwk.models import pwkZZjz, PwkInfo


class DocumentForm(forms.Form):
    docfile=forms.FileField(
        label='选择多个文件',
        widget=forms.FileInput(attrs={'multiple': True})
    )
    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False
        return helper


# 查询条件表单
class QueryListForm(forms.Form):

    def __init__(self,*args, **kwargs):
        super(QueryListForm, self).__init__(*args, **kwargs)


    # 确认情况
    qrqk_option = conf.qrqk_option
    zzqk_option = conf.zzqk_option
    # 乡镇的列表
    XZ_CHOICE = conf.XZ_CHOICE
    hl_choice=conf.hl_choice
    ps_choice=conf.ps_choice
    # 排水性质选项
    psxz_option = conf.psxz_option
    pwkmc = forms.CharField(max_length=50, label="名称", required=False)
    xz = forms.ChoiceField(label="乡镇", required=False, choices=XZ_CHOICE)
    prhlmc=forms.ChoiceField(label="排入河流名称",required=False,choices=hl_choice)
    zzqk = forms.ChoiceField(label="整治情况", required=False, choices=zzqk_option)
    psqk=forms.ChoiceField(label="排水情况",required=False,choices=ps_choice)
    psxz=forms.ChoiceField(label="排水性质",required=False,choices=psxz_option)
    qrqk = forms.ChoiceField(label="确认情况", required=False, choices=qrqk_option)
    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False
        helper.field_template = 'bootstrap3/layout/inline_field.html'
        helper.layout = Layout(
            'pwkmc',
            'xz',
            'prhlmc',
            'zzqk',
            'psqk',
            "psxz",
            'qrqk',
        )
        return helper


# 地图排污口查询条件
class IndexForm(forms.Form):
    def __init__(self,*args, **kwargs):
        super(IndexForm, self).__init__(*args, **kwargs)

    # 确认情况
    qrqk_option=conf.qrqk_option
    # 治理情况
    zzqk_option = conf.zzqk_option
    # 乡镇的列表
    XZ_CHOICE = conf.XZ_CHOICE
    hl_choice=conf.hl_choice

    ps_choice=conf.ps_choice

    pwkmc = forms.CharField(max_length=50, label="名称", required=False)
    xz = forms.ChoiceField(label="乡镇", required=False, choices=XZ_CHOICE)
    prhlmc=forms.ChoiceField(label="排入河流名称",required=False, choices=hl_choice)
    zzqk = forms.ChoiceField(label="整治情况", required=False, choices=zzqk_option)
    psqk=forms.ChoiceField(label="排水情况",required=False, choices=ps_choice)
    qrqk=forms.ChoiceField(label="确认情况",required=False, choices=qrqk_option)
    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False
        helper.field_template = 'bootstrap3/layout/inline_field.html'
        helper.layout = Layout(
            'pwkmc',
            'xz',
            'prhlmc',
            'zzqk',
            'psqk',
        )
        return helper


# 对排污口整治进展的阶段情况提供图片证据，拍摄时间、拍摄人、描述、上传时间等
class ZzjzForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ZzjzForm, self).__init__(*args, **kwargs)
        self.fields['pwkid'].widget=forms.HiddenInput()
        self.fields['pwkmc'].widget.attrs['disabled'] = 'disabled'
    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False
        helper.layout = Layout(
            'pwkid',
            'pwkmc',
            'psr',
            'desc',
            'pwkImage',
        )
        return helper
    class Meta:
        model=pwkZZjz
        fields=['pwkid','pwkmc','psr','desc','pwkImage']


# 整治过程查询统计的条件
class ZzgccxForm(forms.Form):
    def __init__(self,*args, **kwargs):
        super(ZzgccxForm, self).__init__(*args, **kwargs)
    XZ_CHOICE = conf.XZ_CHOICE
    pwkmc = forms.CharField(max_length=50, label="名称", required=False)
    xz = forms.ChoiceField(label="乡镇", required=False, choices=XZ_CHOICE)
    prhlmc=forms.ChoiceField(label="河流名称",required=False,choices=conf.hl_choice)
    start_date=forms.DateField(label="开始日期",required=False,
                               widget=DatePickerInput(format='%Y-%m-%d'))
    end_date=forms.DateField(label="结束日期",required=False,
                             widget=DatePickerInput(format='%Y-%m-%d'))
    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False
        helper.field_template = 'bootstrap3/layout/inline_field.html'
        helper.layout = Layout(
            'pwkmc',
            'xz',
            HTML('<span>开始日期：</span>'),
            'start_date',
            HTML('<span>结束日期：</span>'),
            'end_date',
        )
        return helper


# 排污口修改过程查询条件
class ModifyQueryForm(forms.Form):
    def __init__(self,*args, **kwargs):
        super(ModifyQueryForm, self).__init__(*args, **kwargs)
    XZ_CHOICE = conf.XZ_CHOICE
    pwkmc = forms.CharField(max_length=50, label="名称", required=False)
    xz = forms.ChoiceField(label="乡镇", required=False, choices=XZ_CHOICE)
    start_date=forms.DateField(label="开始日期",required=False, widget=DatePickerInput(format='%Y-%m-%d'))
    end_date=forms.DateField(label="结束日期",required=False, widget=DatePickerInput(format='%Y-%m-%d'))
    @property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False
        helper.field_template = 'bootstrap3/layout/inline_field.html'
        helper.layout = Layout(
            'pwkmc',
            'xz',
            HTML('<span>开始日期：</span>'),
            'start_date',
            HTML('<span>结束日期：</span>'),
            'end_date',
        )
        return helper


# 20181009 优化程序时增加
# 排污口增加和修改的校验
class PwkInfoForm(ModelForm):
    class Meta:
        model = PwkInfo
        exclude = ["bd_jd", "bd_wd", 'qrqk', "syPwkbz"]

    def clean_pwkbm(self):
        pwkbm = self.cleaned_data['pwkbm']
        if 'pwkbm' not in self.changed_data:
            return pwkbm
        qs = PwkInfo.objects.filter(pwkbm=pwkbm)
        if qs.exists():
            raise forms.ValidationError("排污口编码已经存在！")
        return pwkbm

    def clean_pwkmc(self):
        pwkmc = self.cleaned_data['pwkmc']
        if 'pwkmc' not in self.changed_data:
            return pwkmc
        pwkmc = self.cleaned_data['pwkmc']
        qs = PwkInfo.objects.filter(pwkmc=pwkmc)
        if qs.exists():
            raise forms.ValidationError("排污口名称已经存在！")
        return pwkmc

