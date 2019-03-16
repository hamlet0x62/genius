from flask import jsonify, g, request
from flask.blueprints import Blueprint

from flask_login import current_user

from genius.db import db
from genius.db.model import UsersLendBook, User, BookOfUser, Book, UserCollection
from genius.db.file_model import UserBookImage, BookThumbnail, UserAvator
from genius.util.http import api_abort

from genius.util.serialize import jsonify_userlendbook, jsonify_bookofuser, jsonify_usercollection, user_logined
from .forms import fill_form, new_genius_form_schema, new_genius_form
from genius.util.schemas import user_schema, bookofuser_schema

from sqlalchemy import or_


user_api_bp = Blueprint('user_api', __name__, url_prefix="/user/api")
user_api_bp.cors = True
user_api_bp.url_pattern = user_api_bp.url_prefix + '/*'


def query_current_user_lendbooks(*criterions):
    return UsersLendBook.query.filter(UsersLendBook.id == current_user.id, *criterions)


@user_api_bp.route('/borrow_history')
@jsonify_userlendbook
def borrow_history():
    history = query_current_user_lendbooks(not UsersLendBook.is_borrowing).all()
    return history


@user_api_bp.route('/borrowing')
@jsonify_userlendbook
def borrowing():
    return query_current_user_lendbooks(UsersLendBook.is_borrowing).all()


@user_api_bp.route('/lending_genius')
@jsonify_bookofuser
def lending_genius():
    return [book for book in current_user.books_of_user if book.is_lending]


@user_api_bp.route('/blocking_genius')
@jsonify_bookofuser
def blocking_genius():
    return [book for book in current_user.books_of_user if book.blocking]


@user_api_bp.route('/asleep_genius')
@jsonify_bookofuser
def asleep_genius():
    return [book for book in current_user.books_of_user if book.asleep]


@user_api_bp.route('/genius')
@jsonify_bookofuser
def genius():
    return BookOfUser.query.all()


@user_api_bp.route('/current_user_profile')
def current_profile():
    rst = User.query.get(current_user.id)

    if not rst:
        api_abort(404)
    return jsonify(
        {
            'data': rst.to_dict(schema=user_schema)
        }
    )


@user_api_bp.route('/update_avator', methods=['POST'])
def update_avator():
    avator = request.files['avator']
    if avator:
        user_avator = UserAvator.create_from_file(avator)
        current_user.avators = [user_avator]
        current_user.save()
        return jsonify(

            { 
                'data': {
                    'avator_url': user_avator.url
                }
            }
        )

    return api_abort(400, 'Avator file required')



@user_api_bp.route('/new_genius', methods=['POST'])
@fill_form(new_genius_form_schema, new_genius_form)
def new_genius(form: new_genius_form):
    book = Book.query.filter(Book.isbn == form.isbn).first()
    if not book:
        book_info_required = (
            'name', 'author', 'douban_id', 'pub_date', 'publisher', 'img_src'
        )
        if g.data_dict and 'book' in g.data_dict and all([x in g.data_dict['book'] for x in book_info_required]):
            book_info = g.data_dict['book']
            book = Book(name=book_info['name'],
                        other_name=book_info['other_name'],
                        authors=book_info['author'],
                        douban_id=book_info['douban_id'],
                        pub_date=book_info['pub_date'],
                        publisher=book_info['publisher'],
                        isbn=form.isbn)
            book.save()
            # sending retrieve tasks to message queue
            BookThumbnail.retrieve_from_url(book_info['img_src'], book=book)
        else:
            return api_abort(400, 'Book Information required.')
    genius = BookOfUser.create_with_uuid()
    genius.user = current_user
    genius.book_id = book.id
    genius.description = form.description
    genius.deprecation = form.deprecation
    genius.address_id = form.addressId

    photos = UserBookImage.query.filter(or_(*[photo_id == UserBookImage.id for photo_id in form.photoIds])).all()
    if len(photos) == len(form.photoIds):
        genius.imgs = photos
        db.session.add(genius)
        db.session.commit()
        return jsonify(genius.to_dict(schema=bookofuser_schema))
    else:
        db.session.rollback()
        print(photos, form.photoIds)
        return api_abort(400, 'Photos not match.')

    return api_abort(404, message='Book not exists.')


@user_api_bp.route('/collect/<int:book_id>')
def collect(book_id):
    book = Book.query.get_or_404(book_id)
    collection = UserCollection.query.filter(UserCollection.book_id == book.id,
                                             UserCollection.user_id == current_user.id).first()
    msg = ''
    print(collection)
    if not collection:
        collection = UserCollection(book_id=book.id, user_id=current_user.id)
        collection.save()
        msg = '添加'
    else:
        collection.delete()
        msg = '取消'

    return jsonify({
        'data': collection.to_dict(),
        'message': msg + '成功'
    })


@user_api_bp.route('/collection')
@jsonify_usercollection
def collected_book():
    return current_user.collections


@user_api_bp.before_request
def authenticate():
    if not user_logined():
        return api_abort(403, 'Login required.')
