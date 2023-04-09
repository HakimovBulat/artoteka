from flask_wtf import FlaskForm
from wtforms import StringField, FileField, IntegerField, BooleanField, DateField, SubmitField
from wtforms.validators import DataRequired

class OpinionForm(FlaskForm):
    creator = StringField('Создатель', validators=[DataRequired()])
    picture = FileField('Изображение', validators=[DataRequired()])
    about = StringField(validators=[DataRequired()])
    rating = IntegerField('Оценка от 1 до 5', validators=[DataRequired()])
    date = DateField('Дата', validators=[DataRequired()])
    is_watched = BooleanField(validators=[DataRequired()])
    submit = SubmitField('Создать мнение', validators=[DataRequired()])