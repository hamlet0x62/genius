# coding=utf-8
from wtforms import FileField
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from flask_uploads import IMAGES


class BookDetailForm(FlaskForm):
    thumbnail = FileField(label="Thumbnails", validators=[FileRequired(), FileAllowed(IMAGES, u'只能上传图片..')])
