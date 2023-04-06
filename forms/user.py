from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, EmailField, DateField, TextAreaField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    birthday = DateField('День рождения', validators=[DataRequired()])
    about = TextAreaField('О себе', validators=[DataRequired()])
    address = StringField('Откуда вы', validators=[DataRequired()])
    submit = SubmitField('Продолжить')