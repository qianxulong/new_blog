from django.shortcuts import render, redirect, HttpResponse
from django.contrib import auth
from geetest import GeetestLib
# Create your views here.

from django import forms
from app01 import models
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db.models import Count
class Regform(forms.Form):
    # name = forms.CharField(
    #      label="用户名",
    #      max_length=16,
    #      widget=forms.widgets.TextInput(attrs={"class": "form-control"},),
    #      error_messages={ "required": "用户名不能为空",
    #                      "invalid": "格式错误",
    #                      "max_length": "最多输入16位"}
    #  )

    username = forms.CharField(
        # 校验规则相关
        max_length=16,
        label="用户名",
        error_messages={
            "required": "该字段不能为空",
        },
        # widget控制的是生成html代码相关的
        widget=forms.widgets.TextInput(attrs={"class": "form-control"})
    )
    password = forms.CharField(
        label="密码",
        min_length=6,
        max_length=10,
        widget=forms.widgets.PasswordInput(attrs={"class": "form-control"}, render_value=True),
        error_messages={
            "min_length": "密码不能少于6位！",
            "max_length": "密码最长10位！",
            "required": "该字段不能为空",
        }
    )
    re_password = forms.CharField(
        label="确认密码",
        min_length=6,
        max_length=10,
        widget=forms.widgets.PasswordInput(attrs={"class": "form-control"}, render_value=True),
        error_messages={
            "min_length": "密码不能少于6位！",
            "max_length": "密码最长10位！",
            "required": "该字段不能为空",
        }
    )

    email = forms.EmailField(
        label="邮箱",
        widget=forms.widgets.EmailInput(
            attrs={"class": "form-control"},

        ),
        error_messages={
            "invalid": "邮箱格式不正确！",
            "required": "邮箱不能为空",
        }
    )


    def clean(self):
        password = self.cleaned_data.get("password")
        re_password = self.cleaned_data.get("re_password")

        if re_password and re_password != password:
            self.add_error("re_password", ValidationError("两次密码不一致"))

        else:
            return self.cleaned_data

        #全局钩子返回cleaned_data,局部钩子返回编辑的字段


def register(request):
    form_obj = Regform()
    if request.method == "POST":
        form_obj = Regform(request.POST)
        ret = {"status": 0, "msg": ""}

        if form_obj.is_valid():
            print(form_obj.cleaned_data)
            form_obj.cleaned_data.pop("re_password")
            avatar_img = request.FILES.get("avatar")
            models.UserInfo.objects.create_user(**form_obj.cleaned_data,avatar = avatar_img)
            ret["msg"] = "/index/"
            return JsonResponse(ret)
        else:
            print(request.POST.get("name"))
            print(request.POST.get("password"))
            print(form_obj.errors)
            ret["status"] = 1
            ret['msg'] = form_obj.errors
            return JsonResponse(ret)
    return render(request, "register1.html", {"form_obj": form_obj})


def index(request):
    all_article = models.Article.objects.all()
    return render(request,"index.html",{"article_list":all_article})

# 请在官网申请ID使用，示例ID不可使用
pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"

# 处理极验 获取验证码的视图
def get_geetest(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    return HttpResponse(response_str)

def login(request):
    # if request.is_ajax():  # 如果是AJAX请求
    if request.method == "POST":
        # 初始化一个给AJAX返回的数据
        ret = {"status": 0, "msg": ""}
        # 从提交过来的数据中 取到用户名和密码
        username = request.POST.get("username")
        pwd = request.POST.get("password")
        # 获取极验 滑动验证码相关的参数
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE, '')
        validate = request.POST.get(gt.FN_VALIDATE, '')
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session["user_id"]

        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            # 验证码正确
            # 利用auth模块做用户名和密码的校验
            user = auth.authenticate(username=username, password=pwd)
            if user:
                # 用户名密码正确
                # 给用户做登录
                auth.login(request, user)
                ret["msg"] = "/index/"
            else:
                # 用户名密码错误
                ret["status"] = 1
                ret["msg"] = "用户名或密码错误！"
        else:
            ret["status"] = 1
            ret["msg"] = "验证码错误"

        return JsonResponse(ret)
    return render(request, "login.html")

def logout(request):
    auth.logout(request)
    return redirect("/index/")


def home(request,username):
    user =models.UserInfo.objects.filter(username=username).first()
    if not user:
        return HttpResponse("404")
    article_list =models.Article.objects.filter(user=user)
    blog =user.blog
    category = models.Category.objects.filter(blog=blog)
    category_list =category.annotate(num =Count("article")).values("title","num")
    tag_list=models.Tag.objects.filter(blog=blog).annotate(num =Count("article")).values("title","num")
    archive_list = models.Article.objects.filter(user=user).extra(
        select={"archive_ym": "date_format(create_time,'%%Y-%%m')"}
    ).values("archive_ym").annotate(c=Count("nid")).values("archive_ym", "c")

    return render(request,'home.html',
                  {"username":username,
                      "article_list":article_list,
                   "blog":blog,
                   }
                  )

def article_detail(request,username,nid):
    user = models.UserInfo.objects.filter(username=username).first()
    blog = user.blog
    article=models.Article.objects.filter(nid = nid).first()
    article_detail=models.ArticleDetail.objects.filter(article= article).first()
    print(article_detail)
    comment_list=models.Comment.objects.filter(article_id=nid)
    return render(request,'article_detail.html',
                  {"username":username,
                   "blog":blog,
                   "article":article ,
                   "article_detail": article_detail,
                   "comment_list":comment_list,
                   }
                  )

def up_down(request):
    from django.db.models import F
    is_click =request.POST.get("is_click")
    import json
    is_click = json.loads(is_click)
    print(is_click)
    article_id = request.POST.get("article_id")
    user= request.user
    response ={"status":True}
    try:
        models.ArticleUpDown.objects.create(article_id=article_id,user = user,is_up=is_click)
        if is_click:
            print(123)
            models.Article.objects.filter(pk=article_id).update(up_count =F("up_count")+1)
        else:
            print(456)
            models.Article.objects.filter(pk=article_id).update(down_count=F("down_count") + 1)
    except Exception as e:
        response["status"]=False
        response["first_action"]=models.ArticleUpDown.objects.filter(article_id=article_id,user = user).first().is_up
    return JsonResponse(response)
# import json
#
# from django.db.models import F
#
# def up_down(request):
#     print(request.POST)
#     article_id=request.POST.get('article_id')
#     is_up=json.loads(request.POST.get('is_up'))
#     user=request.user
#     response={"state":True}
#     print("is_up",is_up)
#     try:
#         models.ArticleUpDown.objects.create(user=user,article_id=article_id,is_up=is_up)
#         models.Article.objects.filter(pk=article_id).update(up_count=F("up_count")+1)
#
#     except Exception as e:
#         response["state"]=False
#         response["fisrt_action"]=models.ArticleUpDown.objects.filter(user=user,article_id=article_id).first().is_up
#
#     return JsonResponse(response)

def comment(request):
    response ={}
    article_id = request.POST.get("article_id")

    content = request.POST.get("content")
    pid =request.POST.get("pid")
    print(article_id,content,pid)
    user = request.user
    if pid:
        comment_obj =models.Comment.objects.create(article_id=article_id,user =user,content=content,parent_comment_id=pid)
    else:
        comment_obj = models.Comment.objects.create(article_id=article_id, user=user, content=content)
    response["create_time"] =comment_obj.create_time.strftime("%Y-%m-%d")
    #时间对象无法通过json序列化，需转化为字符串
    response["content"] =comment_obj.content
    response["pid"]=comment_obj.parent_comment_id
    response["username"]=comment_obj.user.username
    return JsonResponse(response)


def comment_tree(request,article_id):
    comment = models.Comment.objects.filter(article_id=article_id).values("pk","create_time","content","parent_comment_id","user__username")
    comment_list =list(comment)
    return JsonResponse(comment_list,safe=False)


