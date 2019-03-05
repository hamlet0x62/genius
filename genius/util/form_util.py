from flask import request, redirect, render_template, url_for
from functools import wraps

from genius.errors import FormNotMatchException


def render_form(form_cls, template):
    """
    decorators for flask view functions.
    automatically initialize FlaskForm instance and
    inject form argument to view function
    and render it to target template for GET request,
    view functions with this decorator only needs to
    cope with validate form submits.intercept invalid
    form submit requests, catch FormNotMatchExceptions
    redirect to next_url if 'n' in request's argument
    else return original function's result
    :param form_cls:
    :param template:
    :return:
    """
    def wrapper(view_func):
        @wraps(view_func)
        def _inner(*args, **kws):
            form = form_cls()
            if form.validate_on_submit():
                try:
                    rst = view_func(*args, form=form, **kws)
                    if 'n' in request.args:
                        return redirect(request.args['n'])
                    else:
                        return rst
                except FormNotMatchException:
                    return render_template(template, form=form)

            return render_template(template, form=form)
        return _inner
    return wrapper
