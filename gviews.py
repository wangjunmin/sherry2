# 用通用视图实现的查询统计分析。
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormMixin
from django.views.generic.list import BaseListView, MultipleObjectTemplateResponseMixin

from pwk.forms import IndexForm, QueryListForm

from pwk.utils import get_pwkQuery_set

from pwk.views import dthlChoice

@login_required(login_url='/admin/login/')
class IndexView(TemplateView):
    template_name = "pwk/index.html"
    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        form = IndexForm(self.request.POST or None)
        dthlChoice(self.request, form)
        context['form'] = form
        return context


#查询排污口
class PostListView(BaseListView, MultipleObjectTemplateResponseMixin):
    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()
        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                    'class_name': self.__class__.__name__,
                })
        context = self.get_context_data()
        return self.render_to_response(context)


class QureyPwkView(FormMixin, PostListView):
    form_class = QueryListForm
    template_name = "pwk/pwk_list1.html"
    ordering = 'pwkbm'
    paginate_by = 5

    # 用form 作为查询条件
    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        form = form_class(self.request.POST or None)
        sessionform = self.request.session.get('form', None)
        if self.request.method == 'GET' and sessionform:  # 翻页的处理
            form = sessionform
        else:
            # 把查询条件放在会话中
            self.request.session['form'] = form
        dthlChoice(self.request, form)
        return form


    def get_queryset(self):
        queryset = get_pwkQuery_set(self.request)
        queryset = self._queryDict_(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(QureyPwkView, self).get_context_data(**kwargs)
        form = self.get_form(self.form_class)
        context['form'] = form
        return context

    # 根据条件进行查询
    def _queryDict_(self, queryset):
        form = self.get_form(self.form_class)
        if form.is_valid():
            queryDict = form.cleaned_data
        else:
            return queryset
        pwkmc = queryDict["pwkmc"]
        xz = queryDict["xz"]
        zzqk = queryDict['zzqk']
        prhlmc = queryDict['prhlmc']
        psqk = queryDict['psqk']
        psxz = queryDict['psxz']
        qrqk = queryDict['qrqk']

        pwks = queryset
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
        return pwks



