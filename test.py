import pymysql

from models.comment import Comment
from models.todo import Todo
from models.user import User
from models.session import Session
from models.weibo import Weibo
from utils import random_string
from secret import database_password

# noinspection SqlNoDataSourceInspection,SqlResolve
def test():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password=database_password,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    with connection.cursor() as cursor:
        cursor.execute('DROP DATABASE `web`')
        cursor.execute('CREATE DATABASE `web` CHARACTER SET utf8mb4')
        cursor.execute('USE `web`')

        cursor.execute(User.sql_create)
        cursor.execute(Session.sql_create)
        cursor.execute(Todo.sql_create)
        cursor.execute(Comment.sql_create)
        cursor.execute(Weibo.sql_create)
    connection.commit()
    connection.close()

    form = dict(
        username='dink',
        password='123',
    )
    User.register_user(form)
    u, result = User.login_user(form)
    assert u is not None, result

    session_id = random_string()
    form = dict(
        session_id=session_id,
        user_id=u.id,
    )
    Session.new(form)
    s: Session = Session.one(session_id=session_id)
    assert s.session_id == session_id

    form = dict(
        title='test todo',
        user_id=u.id,
    )
    t = Todo.add(form, u.id)
    assert t.title == 'test todo'


if __name__ == '__main__':
    test()
