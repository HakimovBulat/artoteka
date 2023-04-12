from flask import Flask, render_template, redirect, request, abort
from flask_login import current_user, login_user, login_required, logout_user, LoginManager
from data.opinions import Opinion
from data.users import User
from data import db_session
from forms.user import RegisterForm
from forms.login import LoginForm
from forms.opinion import OpinionForm
from base64 import b64encode as enc64
from base64 import b64decode as dec64
from io import BytesIO
from PIL import Image
import datetime
import pathlib
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init('db/blogs.db')
db_sess = db_session.create_session()
opinion = db_sess.query(Opinion).all()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Главная страница')


login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


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
            surname=form.surname.data, name=form.name.data, 
            email=form.email.data, birthday=form.birthday.data,
            about=form.about.data, address=form.address.data
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

@app.route('/my_page')
def my_page():
    global pictures
    db_sess = db_session.create_session()
    pict = "static\img\pulp_fiction.jpg"
    with open(pict, "rb") as f:
        binary = enc64(f.read())
    #opinion = Opinion(name='Криминальное чтиво', picture=binary, raiting=5, genre='Фильм', about='Самый лучший фильм Тарантино', user_id=current_user.id, date=datetime.date(2023, 3, 3), is_watched=True)
    opinions = db_sess.query(Opinion).filter(Opinion.user_id == current_user.id).all()
    pictures = []
    for opinion in opinions:
        picture = BytesIO(dec64(opinion.picture))
        image = Image.open(picture)
        image.save(f'static\img\{opinion.id}.jpg')
        pictures.append(f'static\img\{opinion.id}.jpg')
    return render_template('my_page.html', title="Моя страница", user=current_user, opinions=opinions)


@app.route('/about')
def about():
    return render_template('about.html', title='О проекте')


@app.route('/opinions',  methods=['GET', 'POST'])
@login_required
def add_opinion():
    form = OpinionForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        opinions = Opinion()
        opinions.name = form.name.data
        opinions.date = form.date.data
        opinions.is_watched = form.is_watched.data
        opinions.rating = form.rating.data
        opinions.about = form.about.data
        opinions.picture = form.picture.data
        opinions.genre = 'Фильм'
        opinions.user_id = current_user.id
        current_user.opinions.append(opinions)
        print(opinions)
        db_sess.merge(current_user)
        print(db_sess)
        db_sess.add(opinions)
        db_sess.commit()
        return redirect('/')

    return render_template('opinion.html', title='Добавление мнения', form=form, current_user=current_user)


@app.route('/opinions/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_opinion(id):
    form = OpinionForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        opinions = db_sess.query(Opinion).filter(Opinion.id == id, Opinion.user == current_user).first()
        if opinions:
            form.opinion.data = opinions.opinion
            form.team_leader.data = opinions.team_leader
            form.is_finished.data = opinions.is_finished
            form.work_size.data = opinions.work_size
            form.collaborators.data = opinions.collaborators

        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        opinions = db_sess.query(opinions).filter(opinions.id == id, opinions.user == current_user).first()
        if opinions:
            opinions = Opinion()
            opinions.name = form.name.data
            opinions.date = form.date.data
            opinions.is_watched = form.is_watched.data
            opinions.rating = form.rating.data
            opinions.about = form.about.data
            opinions.picture = form.picture.data
            opinions.genre = 'Фильм'
            opinions.user_id = current_user.id
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('opinions.html', title='Редактирование работы', form=form)
#
#
#@app.route('/opinions_delete/<int:id>', methods=['GET', 'POST'])
#@login_required
#def news_delete(id):
#    db_sess = db_session.create_session()
#    opinions = db_sess.query(opinions).filter(opinions.id == id, opinions.user == current_user).first()
#    if opinions:
#        db_sess.delete(opinions)
#        db_sess.commit()
#    else:
#        abort(404)
#    return redirect('/')
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
