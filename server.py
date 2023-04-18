from flask import Flask, render_template, redirect, request, abort
from flask_login import current_user, login_user, login_required, logout_user, LoginManager
from data.opinions import Opinion
from data.users import User
from data import db_session
from forms.user import RegisterForm
from forms.login import LoginForm
from forms.opinion import OpinionForm
from base64 import b64encode as enc64, b64decode as dec64
from io import BytesIO
from PIL import Image
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init('db/blogs.db')
db_sess = db_session.create_session()
opinion = db_sess.query(Opinion).all()

@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    opinions = db_sess.query(Opinion).filter(Opinion.is_secret == 1).all()[-5:]
    return render_template('index.html', title='Главная страница', opinions=opinions)


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


@app.route('/opinions/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_opinion(id):
    form = OpinionForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        opinions = db_sess.query(Opinion).filter(Opinion.id == id, Opinion.user == current_user).first()
        if opinions:
            form.name.data = opinions.name
            form.date.data = opinions.date
            form.is_secret.data = opinions.is_secret
            form.rating.data = opinions.raiting
            form.about.data = opinions.about
            form.genre.data = opinions.genre
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        opinions = db_sess.query(Opinion).filter(Opinion.id == id, Opinion.user == current_user).first()
        if opinions:
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
        else:
            abort(404)
    return render_template('opinion.html', title='Редактирование мнения', form=form)


@app.route('/opinions_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def opinions_delete(id):
    db_sess = db_session.create_session()
    opinion = db_sess.query(Opinion).filter(Opinion.id == id, Opinion.user == current_user).first()
    if opinion:
        db_sess.delete(opinion)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/my_page')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    for picture in pictures:
        os.remove(picture)