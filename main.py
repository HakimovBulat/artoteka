from flask import Flask, render_template, redirect
from flask_login import current_user, login_user, login_required, logout_user, LoginManager
from data.opinions import Opinion
from data.users import User
from data import db_session
from forms.user import RegisterForm
from forms.login import LoginForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init('db/blogs.db')


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
    db_sess = db_session.create_session()
    opinions = db_sess.query(Opinion).filter(Opinion.user_id == current_user.id).all()
    return render_template('my_page.html', title="Моя страница", user=current_user, opinions=opinions)

@app.route('/about')
def about():
    return render_template('about.html', title='О проекте')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')