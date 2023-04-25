from flask import Flask, render_template, redirect, request, make_response, jsonify
from flask_login import current_user, login_user, login_required, logout_user, LoginManager
from data.opinions import Opinion
from data.users import User
from data import db_session, opinions_api
from forms.user import RegisterForm
from forms.login import LoginForm
from forms.opinion import OpinionForm
from base64 import b64encode as enc64, b64decode as dec64
from io import BytesIO
from PIL import Image
import os
import shutil
import pymorphy2


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['JSON_AS_ASCII'] = False
db_session.global_init('db/blogs.db')
morph = pymorphy2.MorphAnalyzer()

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader


def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    opinions = db_sess.query(Opinion).filter(Opinion.is_secret == 1).all()[-10:]
    opinions.reverse()
    for opinion in opinions:
        if opinion.picture != b'':
            picture = BytesIO(dec64(opinion.picture))
            image = Image.open(picture)
            image.save(f'static\img\downloads\{opinion.id}.jpg')
        else:
            image = Image.open('static\img\problem_image.jpg')
            image.save(f'static\img\downloads\{opinion.id}.jpg')
    return render_template('index.html', title='Главная страница', opinions=opinions)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', 
                                   form=form, message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data, 
            name=form.name.data, 
            email=form.email.data, 
            birthday=form.birthday.data,
            about=form.about.data, 
            address=form.address.data
            )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', title='Войти', form=form, message='Неправильный логин или пароль')
    return render_template('login.html', title='Войти', form=form)


@app.route('/another_page-<int:id>')
@app.route('/another_page-<int:id>-<genre>')
def another_page(id, genre=''):
    genres = {'movies': 'Фильм', 'series': "Сериал", 'songs': 'Песня', '': ['Фильм', 'Сериал', 'Песня']}
    genre = genres[genre]
    db_sess = db_session.create_session()
    opinions = db_sess.query(Opinion).filter(Opinion.user_id == id, Opinion.is_secret == 1).all()
    try:
        for opinion in opinions:
            if opinion.picture != b'':
                picture = BytesIO(dec64(opinion.picture))
                image = Image.open(picture)
                image.save(f'static\img\downloads\{opinion.id}.jpg')
            else:
                image = Image.open('static\img\problem_image.jpg')
                image.save(f'static\img\downloads\{opinion.id}.jpg')
        user_name = morph.parse(opinions[0].user.name)[0].inflect({'gent'}).word.capitalize()
        user_surname = morph.parse(opinions[0].user.surname)[0].inflect({'gent'}).word.capitalize()
        return render_template('my_page.html', title=f"Страница {user_surname} {user_name}",
                                user=current_user, id=opinions[0].user.id, opinions=opinions, genre=genre)
    except Exception:
        return render_template('error.html', title='Ошибка')


@app.route('/my_page')
@app.route('/my_page-<genre>')
@login_required
def my_page(genre=''):
    global pictures
    genres = {'movies': 'Фильм', 'series': "Сериал", 'songs': 'Песня', '': ['Фильм', 'Сериал', 'Песня']}
    genre = genres[genre]
    db_sess = db_session.create_session()
    opinions = db_sess.query(Opinion).filter(Opinion.user_id == current_user.id).all()
    try:
        for opinion in opinions:
            if opinion.picture != b'':
                picture = BytesIO(dec64(opinion.picture))
                image = Image.open(picture)
                image.save(f'static\img\downloads\{opinion.id}.jpg')
            else:
                image = Image.open('static\img\problem_image.jpg')
                image.save(f'static\img\downloads\{opinion.id}.jpg')
        return render_template('my_page.html', title="Моя страница", user=current_user, 
                               opinions=opinions, genre=genre, id=current_user.id)
    except Exception:
        return render_template('error.html', title='Ошибка')


@app.route('/about')
def about():
    return render_template('about.html', title='О проекте')


@app.route('/opinions',  methods=['GET', 'POST'])
@login_required
def add_opinion():
    form = OpinionForm()    
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        opinions = Opinion(
            name = form.name.data,
            date = form.date.data,
            is_secret = form.is_secret.data, 
            raiting = form.rating.data,
            about = form.about.data, 
            picture = enc64(request.files['file'].read()),
            genre = form.genre.data, 
            user_id = current_user.id)
        current_user.opinions.append(opinions)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/my_page')
    return render_template('opinion.html', title='Добавление мнения', form=form, current_user=current_user)


@app.route('/opinions-<int:id>', methods=['GET', 'POST'])
def edit_opinion(id):
    form = OpinionForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        opinions = db_sess.query(Opinion).filter(Opinion.id == id, Opinion.user == current_user).first()
        try:
            form.name.data = opinions.name
            form.date.data = opinions.date
            form.is_secret.data = opinions.is_secret
            form.rating.data = opinions.raiting
            form.about.data = opinions.about
            form.genre.data = opinions.genre
        except Exception:
            return render_template('error.html', title='Ошибка')
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        opinions = db_sess.query(Opinion).filter(Opinion.id == id, Opinion.user == current_user).first()
        try:
            opinions.name = form.name.data
            opinions.date = form.date.data
            opinions.is_secret = form.is_secret.data
            opinions.raiting = form.rating.data
            opinions.about = form.about.data
            opinions.picture = enc64(request.files['file'].read())
            opinions.genre = form.genre.data
            opinions.user_id = current_user.id
            db_sess.commit()
            return redirect('/my_page')
        except Exception:
            return render_template('error.html', title='Ошибка')
    return render_template('opinion.html', title='Редактирование мнения', form=form)


@app.route('/opinions_delete-<int:id>', methods=['GET', 'POST'])
@login_required
def opinions_delete(id):
    db_sess = db_session.create_session()
    opinion = db_sess.query(Opinion).filter(Opinion.id == id, Opinion.user == current_user).first()
    try:
        db_sess.delete(opinion)
        db_sess.commit()
    except Exception:
        return render_template('error.html', title='Ошибка')
    return redirect('/my_page')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.register_blueprint(opinions_api.blueprint)
    app.run(host='0.0.0.0', port=port)
    shutil.rmtree('static\img\downloads')
    os.mkdir("static\img\downloads")