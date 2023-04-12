from flask_wtf import FlaskForm
from wtforms import StringField, FileField, IntegerField, BooleanField, DateField, SubmitField, SelectField
from wtforms.validators import DataRequired

class OpinionForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    picture = FileField('Изображение', validators=[DataRequired()])
    about = StringField(validators=[DataRequired()])
    rating = IntegerField('Оценка от 1 до 5', validators=[DataRequired()])
    date = DateField('Дата', validators=[DataRequired()])
    is_watched = BooleanField(validators=[DataRequired()])
    genre = SelectField('Жанр', choices=[('Фильм', 'Фильм'), ('Сериал', 'Сериал'), ('Песня', 'Песня')], validators=[DataRequired()])
    submit = SubmitField('Создать мнение', validators=[DataRequired()])