from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    content = TextAreaField('Расскажите о чём-нибудь', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')
