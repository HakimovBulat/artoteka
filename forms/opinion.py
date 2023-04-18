from flask_wtf import FlaskForm
from wtforms import StringField, FileField, IntegerField, BooleanField, DateField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired

class OpinionForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    about = TextAreaField('О фильме')
    rating = IntegerField('Оценка от 1 до 5', validators=[DataRequired()])
    date = DateField('Дата')
    is_secret = BooleanField('Сделать мнение видным для всех')
    genre = SelectField('Жанр', choices=[('Фильм', 'Фильм'), ('Сериал', 'Сериал'), ('Песня', 'Песня')])
    submit = SubmitField('Создать мнение')