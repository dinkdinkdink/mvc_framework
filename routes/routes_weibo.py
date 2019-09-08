from models.comment import Comment
from models.weibo import Weibo
from routes.routes_basic import (
    redirect,
    current_user,
    html_response,
    login_required,
)
from utils import log


def index(request):
    """
    weibo 首页的路由函数
    """
    u = current_user(request)
    weibos = Weibo.all(user_id=u.id)
    # 替换模板文件中的标记字符串
    return html_response('weibo_index.html', weibos=weibos, user=u)


def add(request):
    """
    用于增加新 weibo 的路由函数
    """
    u = current_user(request)
    form = request.form()
    Weibo.add(form, u.id)
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/weibo/index')


def delete(request):
    weibo_id = int(request.query['weibo_id'])
    Weibo.delete(weibo_id)
    return redirect('/weibo/index')


def edit(request):
    weibo_id = int(request.query['weibo_id'])
    w = Weibo.one(id=weibo_id)
    return html_response('weibo_edit.html', weibo=w)


def update(request):
    """
    用于增加新 weibo 的路由函数
    """
    form = request.form()
    weibo_id = int(form['weibo_id'])
    Weibo.update(weibo_id, content=form['content'])
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/weibo/index')


def comment_add(request):
    u = current_user(request)
    form = request.form()
    Comment.add(form, u.id)
    log('comment add')
    return redirect('/weibo/index')


def comment_edit(request):
    comment_id = int(request.query['comment_id'])
    c = Comment.one(id=comment_id)
    return html_response('comment_edit.html', comment=c)


def comment_update(request):
    form = request.form()
    log('tst form', form)
    comment_id = int(form['comment_id'])
    Comment.update(comment_id, content=form['content'])
    return redirect('/weibo/index')


def weibo_owner_required(route_function):
    """
    这个函数看起来非常绕，所以你不懂也没关系
    就直接拿来复制粘贴就好了
    """

    def f(request):
        log('weibo_owner_required')
        u = current_user(request)
        id_key = 'weibo_id'
        if id_key in request.query:
            weibo_id = request.query[id_key]
        else:
            weibo_id = request.form()[id_key]
        w = Weibo.one(id=int(weibo_id))

        if w.user_id == u.id:
            return route_function(request)
        else:
            return redirect('/weibo/index')

    return f


# 用于修改与更新
def comment_owner_required(route_function):
    def f(request):
        log('comment_owner_required')
        u = current_user(request)
        # 查询评论id
        id_key = 'comment_id'
        if id_key in request.query:
            comment_id = request.query[id_key]
        else:
            comment_id = request.form()[id_key]
        c = Comment.one(id=int(comment_id))

        if c.user_id == u.id:
            return route_function(request)
        else:
            return redirect('/weibo/index')

    return f


# 用于删除
def comment_or_weibo_owner_required(route_function):
    def f(request):
        log('comment_owner_required')
        u = current_user(request)
        # 查询评论id，识别用户
        id_key = 'comment_id'
        if id_key in request.query:
            comment_id = request.query[id_key]
        else:
            comment_id = request.form()[id_key]
        c = Comment.one(id=int(comment_id))
        w_id = c.weibo_id
        w = Weibo.one(id=int(w_id))
        # 判断评论用户
        if c.user_id == u.id:
            comment_owner = True
        else:
            comment_owner = False
        # 判断微博用户
        if w.user_id == u.id:
            weibo_owner = True
        else:
            weibo_owner = False

        if comment_owner or weibo_owner:
            return route_function(request)
        else:
            return redirect('/weibo/index')

    return f


def route_dict():
    """
    路由字典
    key 是路由(路由就是 path)
    value 是路由处理函数(就是响应)
    """
    d = {
        '/weibo/index': login_required(index),
        '/weibo/add': login_required(add),
        '/weibo/delete': login_required(weibo_owner_required(delete)),
        '/weibo/edit': login_required(weibo_owner_required(edit)),
        '/weibo/update': login_required(weibo_owner_required(update)),
        # 评论功能
        '/comment/add': login_required(comment_add),
        '/comment/edit': comment_owner_required(comment_edit),
        '/comment/update': comment_or_weibo_owner_required(comment_update),
    }
    return d
