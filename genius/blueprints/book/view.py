from flask import request, render_template, redirect, url_for, abort, jsonify, current_app
from flask import blueprints as bp
from flask import flash

from flask_login import login_required, current_user
from flask_cors import cross_origin

from genius.db import db
from genius.db.model import Book, BookOfUser
from genius.db.file_model import BookThumbnail, BookDetailImage, UserBookImage
from genius.ext.login_manager import login_manager
from genius.ext.principal import edit_userbook_permission, user_role_permission
from genius.util.form_util import render_form
from genius.util.view_util import gen_bp_id_rquired

from functools import wraps

from sqlalchemy import or_

from .forms import PostBookImageForm, PostBookForm

book_bp = bp.Blueprint('book', __name__, url_prefix='/b')
book_bp_id_required = gen_bp_id_rquired(book_bp)


def render(template: str):
    def outer(func):
        @wraps(func)
        def wrapper(*args, **kws):
            render_ctx = {}
            func(render_ctx, *args, **kws)
            return render_template(template, **render_ctx)

        return wrapper

    return outer


@book_bp.route('/uploads', methods=['POST', 'GET'])
def upload():
    flash('Now able to alter books.')
    render_dict = {}
    render_dict.setdefault('books', Book.query.all())
    if request.method == 'POST':
        thumbnail, detail_img, target = request.files.get('img'), request.files.get('detail_img'), \
                                        request.form.get('target', type=int)

        if target:
            book = Book.create_or_get(id=target)
            if thumbnail:
                thumbnail = BookThumbnail.create_from_file(thumbnail)
                thumbnail.rsize(200, 200)
                book.thumbnails = [thumbnail]
            if detail_img:
                detail_img = BookDetailImage.create_from_file(detail_img)
                detail_img.rsize(200, 300)
                book.detail_imgs = ([detail_img])
            book.save()
            detail_img_dict = detail_img.to_dict() if detail_img else None
            thumbnail_dict = thumbnail.to_dict() if thumbnail else None
            render_dict.setdefault('uploaded_imgs', [detail_img_dict or book.detail_imgs[0].to_dict(),
                                                     thumbnail_dict or book.thumbnails[0].to_dict()])
    return render_template('alter_book.j2', **render_dict)


@book_bp.route('/all')
@render('view_book.j2')
def all_books(render_ctx: dict):
    book = Book.query.order_by(Book.create_at.desc()).first()
    render_ctx.setdefault('books', [book])


@book_bp_id_required('bid')
@render('book_detail.j2')
def detail(render_dict, bid):
    render_dict.setdefault('book', Book.query.get_or_404(bid))


@book_bp.route('/post', methods=['POST'])
@login_required
@cross_origin()
def post_book():
    photos = request.files['photos']
    if photos:
        photo = UserBookImage.create_from_file(photos)

        return jsonify({
            'r': 1,
            'photoId': photo.id
        })

    abort(422)

