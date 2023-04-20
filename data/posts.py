import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Posts(SqlAlchemyBase, SerializerMixin):

    created_date_str = str(datetime.datetime.now())
    date_time_obj = datetime.datetime.strptime(created_date_str, '%Y-%m-%d %H:%M:%S.%f')
    date = date_time_obj.date()
    time_all = date_time_obj.time()
    time_right = str(time_all).split(".")[0]
    created_date_dt = f"{date} в {time_right}"

    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.String,
                                     default=created_date_dt)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')

    def __repr__(self):
        return f"{self.content} {self.created_date} {self.user.name} {self.user.surname}"