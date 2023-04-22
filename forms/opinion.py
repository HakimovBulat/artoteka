from flask_wtf import FlaskForm
from wtforms import StringField, FileField, IntegerField, BooleanField, DateField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, NumberRange

class OpinionForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    about = TextAreaField('Ваши впечатления')
    rating = IntegerField('Оценка от 1 до 5', validators=[DataRequired(), NumberRange(min=1, max=5)])
    date = DateField('Когда посмотрели/послушали')
    is_secret = BooleanField('Сделать мнение видным для всех')
    genre = SelectField('Жанр', choices=[('Фильм', 'Фильм'), ('Сериал', 'Сериал'), ('Песня', 'Песня')])
    submit = SubmitField('Создать мнение')