from flask import jsonify, Blueprint, request
from . import db_session
from .opinions import Opinion


blueprint = Blueprint(
    'opinions_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/opinions')
def get_opinions():
    db_sess = db_session.create_session()
    opinions = db_sess.query(Opinion).all()
    return jsonify(
        {
            'opinions':
                [item.to_dict(only=('name', 'raiting', 'genre', 'about', 'date', 'is_secret', 'user.name', 'picture')) 
                 for item in opinions]
        }
    )


@blueprint.route('/api/opinions/<int:opinions_id>', methods=['GET'])
def get_one_opinions(opinions_id):
    db_sess = db_session.create_session()
    opinions = db_sess.query(Opinion).get(opinions_id)
    if not opinions:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'opinions': opinions.to_dict(only=(
                'name', 'raiting', 'genre', 'about', 'date', 'is_secret', 'user_id', 'picture'))
        }
    )


@blueprint.route('/api/opinions', methods=['POST'])
def create_opinions():
    if not request.json:
        return jsonify({'error': 'Empty request'})
    elif not all(key in request.json for key in
                 ['name', 'raiting', 'genre', 'about', 'date', 'is_secret', 'user_id', 'picture']):
        return jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    opinions = Opinion(
        name=request.json['name'],
        date=request.json['date'],
        is_secret=request.json['is_secret'], 
        raiting=request.json['rating'],
        about=request.json['about'], 
        picture=request.json['picture'],
        genre=request.json['genre'],
        user_id=request.json['user_id']
        )
    db_sess.add(opinions)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/opinions/<int:news_id>', methods=['DELETE'])
def delete_news(news_id):
    db_sess = db_session.create_session()
    opinions = db_sess.query(Opinion).get(news_id)
    if not opinions:
        return jsonify({'error': 'Not found'})
    db_sess.delete(opinions)
    db_sess.commit()
    return jsonify({'success': 'OK'})