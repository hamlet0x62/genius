# coding=utf-8
from wtforms import StringField, FileField, MultipleFileField, SelectField, IntegerField, FieldList
from wtforms import validators
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired
from flask_uploads import IMAGES

DEPRECATION_DESCRIPTION = [f'{deprecation}成新' for deprecation in range(5, 10)]
BOOK_DEPRECATION_ITEM = {
    str(value): label for label, value in zip(DEPRECATION_DESCRIPTION, range(len(DEPRECATION_DESCRIPTION)))
}


class BookDetailForm(FlaskForm):
    thumbnail = FileField(label="Thumbnails", validators=[FileRequired(), FileAllowed(IMAGES, u'只能上传图片..')])


class PostBookImageForm(FlaskForm):
    photos = FileField(label='请上传相关图片', validators=[FileRequired(), FileAllowed(IMAGES, message=u'请上传图片')])


class PostBookForm(FlaskForm):
    photos = FieldList(IntegerField(label=u"已上传的图片", validators=[validators.required(), ]))
    isbn = IntegerField(label=u'ISBN', validators=[validators.required()])
    deprecation_rate = IntegerField(label=u'折旧率', validators=[validators.required(), validators.number_range(0, 100)])
    description = StringField(label=u'简单的描述几句')
