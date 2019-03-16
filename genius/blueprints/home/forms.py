from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Email, DataRequired
from genius.db.model import User
from .errors import FormNotMatchException, AuthenticationException


class MatchDBForm(FlaskForm):

    def match_db(self):
        """
        to tell the view functions whether the form is match or not
        :return: Model Type if match else return None type
        """
        if not self.validate_on_submit():
            raise FormNotMatchException("Should validate form first before using match_db method")
        rst = self._match()
        if rst:
            return rst
        else:
            raise AuthenticationException("Form instance is not matched to db model")

    def _match(self):
        raise NotImplementedError("subclasses of MatchDbForm should implement _match function first")


class LoginForm(MatchDBForm):
    email = StringField(label="Email:", validators=[Email(), DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])

    def _match(self):
        user = User.query.filter(User.email == self.email.data).first()
        if current_app.debug:  # return one user anyway in debug mode
            return User.query.first()
        if user and self.password.data == user.password:
            return user
        else:
            self.password.errors.append(u'密码/用户名错误')
