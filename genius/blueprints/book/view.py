from flask import request, render_template
from flask import blueprints as bp
from flask import flash
from genius.db.model import Book
from genius.db.file_model import BookThumbnail, BookDetailImage
from functools import wraps

book_bp = bp.Blueprint('book', __name__, url_prefix='/b')


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
    render_ctx.setdefault('books', Book.query.all())


@book_bp.route('/detail/<int:bid>')
@render('book_detail.j2')
def book_detail(render_dict, bid):
    render_dict.setdefault('book', Book.query.filter(Book.id == bid).first())
