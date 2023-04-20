from flask import jsonify
from flask_restful import reqparse, abort, Resource

from data import db_session
from data.posts import Posts
from data.users import User

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('surname', required=True)
parser.add_argument('email', required=True)
parser.add_argument('date_of_birth', required=True)
parser.add_argument('created_date', required=True)


def abort_if_post_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UserResource(Resource):
    def get(self, user_id):
        abort_if_post_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('name', 'surname', 'email', 'date_of_birth', 'created_date'))})

    def delete(self, user_id):
        abort_if_post_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        posts = session.query(Posts).filter(Posts.user_id == user_id).all()
        if posts:
            for post in posts:
                session.delete(post)
            session.commit()
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'user': [item.to_dict(
            only=('name', 'surname', 'email', 'date_of_birth', 'created_date')) for item in users]})
