import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Opinion(SqlAlchemyBase):
    __tablename__ = 'Opinions'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    creator = sqlalchemy.Column(sqlalchemy.String)
    picture = sqlalchemy.Column(sqlalchemy.BLOB, nullable=True)
    raiting = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    genre = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    date = sqlalchemy.Column(sqlalchemy.Date, default=datetime.datetime.now)
    is_watched = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    user = orm.relationship('User')

    def __repr__(self):
        return f'<Opinion> {self.name}'