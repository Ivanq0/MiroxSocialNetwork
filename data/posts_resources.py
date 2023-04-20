from flask import jsonify
from flask_restful import reqparse, abort, Resource

from data import db_session
from data.posts import Posts

parser = reqparse.RequestParser()
parser.add_argument('content', required=True)
parser.add_argument('created_date', required=True)
parser.add_argument('user_id', required=True, type=int)


def abort_if_post_not_found(post_id):
    session = db_session.create_session()
    post = session.query(Posts).get(post_id)
    if not post:
        abort(404, message=f"Post {post_id} not found")


class PostResource(Resource):
    def get(self, post_id):
        abort_if_post_not_found(post_id)
        session = db_session.create_session()
        post = session.query(Posts).get(post_id)
        return jsonify({'post': post.to_dict(
            only=('content', 'created_date', 'user_id'))})

    def delete(self, post_id):
        abort_if_post_not_found(post_id)
        session = db_session.create_session()
        post = session.query(Posts).get(post_id)
        session.delete(post)
        session.commit()
        return jsonify({'success': 'OK'})


class PostListResource(Resource):
    def get(self):
        session = db_session.create_session()
        posts = session.query(Posts).all()
        return jsonify({'post': [item.to_dict(
            only=('content', 'created_date', 'user_id')) for item in posts]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        post = Posts(
            content=args['content'],
            user_id=args['user_id'],
            created_date=args['created_date']
        )
        session.add(post)
        session.commit()
        return jsonify({'success': 'OK'})
