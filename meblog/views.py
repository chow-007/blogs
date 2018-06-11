
from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse
import re
import json
from meblog import models
from django import forms
from django.forms import widgets
from django.core.exceptions import ValidationError
from utils.random_code import Captcha
from django.db.models import Count, F

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


class FormLogin(forms.Form):
    """
    表单验证
    """

    username = forms.CharField(max_length=16, min_length=6,
                               error_messages={
                                   "required": "不能为空",
                                   "max_length": "用户名长度不能大于16位",
                                   "min_length": "用户名长度不能小于6位",
                               },
                               widget=widgets.TextInput(attrs={"class": "form-control"}),
                               )

    password = forms.CharField(max_length=16, min_length=6,
                               error_messages={
                                   "required": "不能为空",
                                   "max_length": "密码长度不能超过16位",
                                   "min_length": "密码长度不能少于6位",
                               },
                               widget=widgets.PasswordInput(attrs={"class": "form-control"}),
                               )

    repeat_pwd = forms.CharField(
                                 error_messages={
                                     "required": "不能为空",
                                     "max_length": "密码长度不能超过16位",
                                     "min_length": "密码长度不能少于6位",
                                 },
                                 widget=widgets.PasswordInput(attrs={"class": "form-control"}),
                                 )

    email = forms.EmailField(error_messages={"required": "不能为空",
                                             "invalid": "邮箱格式不正确"},
                             widget=widgets.EmailInput(attrs={"class": "form-control"})
                             )

    telephone = forms.CharField(required=False,     # 可以为空
                                error_messages={"required": "不能为空"},
                                widget=widgets.TextInput(attrs={"class": "form-control"}),
                                )

    # 验证用户名是否注册
    def clean_username(self):
        val = self.cleaned_data.get('username')
        is_user = models.UserInfo.objects.filter(username=val)
        if is_user:
            raise ValidationError("用户名已注册")
        else:
            return val

    # 验证手机号是否符合规则
    def clean_telephone(self):
        val = self.cleaned_data.get('telephone')
        res = re.search('^1[345678]\d{9}$', str(val))
        if val:     # 如果手机号为空,就不判断(手机号可以为空,为空不校验,不为空就校验)
            if len(val) == 11:
                if res:
                    return val
                else:
                    raise ValidationError("手机号格式错误")
            else:
                raise ValidationError("手机号长度为11位数字")
        else:return val

    # 验证密码是否一致
    def clean(self):
        val_first = self.cleaned_data.get('password')
        val_second = self.cleaned_data.get('repeat_pwd')
        if val_first == val_second:
            return self.cleaned_data        # 全局钩子返回的是cleaned_data字典
        else:
            raise ValidationError("两次输入的密码不一致")


def home(request):
    """
    主页
    :return: 渲染主页
    """
    article_list = models.Article.objects.filter(nid__lt=10)
    return render(request, 'home.html', {"article_list": article_list})


def reg(request):
    """
    注册
    """
    if request.method == 'POST':
        reg_response = {'user': None, 'error_msg': None}
        # 实例化绑定数据的表单对象
        form_obj = FormLogin(request.POST)
        if form_obj.is_valid():
            username = form_obj.cleaned_data.get('username')
            password = form_obj.cleaned_data.get('password')
            email = form_obj.cleaned_data.get('email')
            telephone = form_obj.cleaned_data.get('telephone')
            avatar_obj = request.FILES.get('avatar')
            # 往数据库写入数据
            user_obj = models.UserInfo.objects.create_user(username=username,
                                                           password=password,
                                                           email=email,
                                                           telephone=telephone,
                                                           avatar=avatar_obj)
            user_obj.save()
            # 此时errors里面是空的,前端拿到errors,通过判断,可以知道用户数据输入正确,执行相应的操作
            reg_response['user'] = user_obj.username
        else:
            # 用户输入错误,把错误信息添加到字典里面
            reg_response['error_msg'] = form_obj.errors
        return HttpResponse(json.dumps(reg_response))
    form_obj = FormLogin()
    return render(request, 'reg.html', {'form_obj': form_obj})


random_str = ''


def captcha(request):
    font_file = "meblog/static/font/kumo.ttf"
    image = Captcha(font_file)
    global random_str
    random_str = image.get_rand_code()
    request.session["random_str"] = random_str
    image_code = image.get_image()
    return HttpResponse(image_code)


def log_in(request):
    """
    登录
    error:定义的一个错误信息容器
    """
    login_response = {'error': '', 'url': '/'}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        valid_code = request.POST.get('valid_code')
        user_obj = authenticate(username=username, password=password)
        if valid_code.upper() == random_str.upper():
            if user_obj:
                login(request, user_obj)
                redirect_url = request.GET.get('next')
                if redirect_url:
                    login_response['url'] = '{}'.format(redirect_url)
                    return HttpResponse(json.dumps(login_response))
                else:
                    return HttpResponse(json.dumps(login_response))
            else:
                login_response['error'] = '用户名或密码错误'
        else:
            login_response['error'] = '验证码错误'
        return HttpResponse(json.dumps(login_response))
    return render(request, 'log_in.html')


def log_out(request):
    """
    用户注销登录
    """
    logout(request)
    return redirect(reverse('login'))


# @login_required
def index(request):
    return render(request, 'index.html')


def blog_site(request, username, **kwargs):
    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse('Not Found')
    if not kwargs:
        article_list = models.Article.objects.filter(user=user)

    else:
        conditions = kwargs.get('conditions')
        params = kwargs.get('params')
        if conditions == "cate":
            article_list = models.Article.objects.filter(user=user, homeCategory__title=params)
        elif conditions == "tag":
            article_list = models.Article.objects.filter(user=user, tags__title=params)
        else:
            year, month = params.split('-')
            print(year, month)
            article_list = models.Article.objects.filter(user=user).filter(create_time__year=year, create_time__month=month)
    blog = user.blog
    category_list = models.HomeCategory.objects.filter(blog=blog)\
        .annotate(c=Count("article"))\
        .values_list("title", 'c')

    tag_list = models.Tag.objects.filter(blog=blog).\
        annotate(n=Count("article"))\
        .values_list("title", "n")

    date_list = models.Article.objects.filter(user=user)\
        .extra(select={"time_tuple": "strftime('%%Y-%%m', create_time)"}).values("time_tuple")\
        .annotate(n=Count("nid")).values_list("time_tuple", "n")

    return render(request, 'blog_site.html', locals())


def article(request, username, article_id):
    content_obj = models.ArticleDetail.objects.filter(article=article_id).first()
    article_obj = models.Article.objects.filter(nid=article_id).first()
    return render(request, 'article_detail.html', locals())


from django.db import transaction
from django.http import JsonResponse
from django.db.utils import IntegrityError


def thumbs(request):
    is_up = json.loads(request.POST.get('is_up'))       # 后端拿到前端的true是字符串, 要用json反序列化
    article_id = request.POST.get('article_id')
    user_id = request.user.pk
    response = {'state': True}

    try:
        with transaction.atomic():
            models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
            if is_up:
                models.Article.objects.filter(nid=article_id).update(up_count=F('up_count') + 1)
            else:
                models.Article.objects.filter(nid=article_id).update(down_count=F('down_count') + 1)
    except IntegrityError as e:
        print('cuole')
        obj = models.ArticleUpDown.objects.filter(user_id=user_id).first()
        print("obj.is_up", obj.is_up)
        response['state'] = False
        response['error_first'] = obj.is_up

    return JsonResponse(response)


from django.core import serializers
def comment(request):
    # if request.method == 'POST':
    #     article_id = request.POST.get('article_id')
    #     content = request.POST.get('content')
    #     user_id = request.user.pk
    #     print(article_id,user_id,content)
    #     # models.Comment.objects.create(content='111', article_id='1', user_id='10')
    #     comment = models.Comment.objects.create(content=content, article_id=article_id, user_id=user_id)
    article_id = int(request.POST.get('article_id'))
    temp = models.Comment.objects.filter(article_id=article_id)\
        .extra(select={"time": "strftime('%%Y-%%m-%%d %%H:%%M:%%f', create_times)"})\
        .values('time', 'nid', 'content', 'parent_comment_id', 'user__username','user__avatar')  # query_set对象
    comment_list = list(temp)
    print("comment_list", comment_list)
    return HttpResponse(json.dumps(comment_list))
