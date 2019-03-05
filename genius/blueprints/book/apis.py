from flask.blueprints import Blueprint

from genius.util.serialize import jsonify_bookofuser
from genius.util.view_util import gen_bp_id_rquired
from genius.db.model import Book

book_api = Blueprint('book_api', __name__, url_prefix='/b/api')

book_api.cors = True
book_api.url_pattern = book_api.url_prefix + '/*'

book_api_id_required = gen_bp_id_rquired(book_api)


@book_api_id_required(id_label='book_id')
@jsonify_bookofuser
def book_copies(book_id):
    book = Book.query.get_or_404(book_id)
    return book.copies
