import pytest
from genius.db.file_model import BookThumbnail
from genius.db import *


@pytest.fixture(scope='module')
def ctx(app):
    return app.app_context()


class TestDB:

    def test_post_book(self, ctx):
        with ctx:
            simon = User.query.first()
            book = Book.query.first()
            book_of_user = simon.post_book(book)
            assert book_of_user is not None
            assert book_of_user.user == simon
            assert book_of_user.book == book

    def test_lend_book(self, ctx):
        with ctx:
            jerry = User.query.first()
            book_of_user = BookOfUser.query.first()

            record = jerry.lend_book(branch=Branch.query.first(),
                                     book_copy=book_of_user)

            assert record is not None
            assert record.lend_user == jerry

            record_2 = jerry.lend_book(branch=Branch.query.first(), book_copy=book_of_user)
            assert record_2 is None

    def test_lender_ensure(self, ctx):
        with ctx:
            records = self.lend_records
            for r in records:
                assert r.state == BookLendState.WAIT
                r._lender_ensure_this()
                r.state = BookLendState.WAIT
            self.jerry.ensure_lending(lend_records=records)
            UsersLendBook.save_all(records)
            assert all([r.state == BookLendState.LENDING
                        for r in records])

    def test_return_books(self, ctx):
        with ctx:
            jerry = self.jerry
            records = self.lend_records
            for r in records:
                r.state = BookLendState.LENDING
                r.save()
            records = jerry.return_books(lend_records=self.lend_records)

            assert records is not None
            assert all([rec.state == BookLendState.BACKING for
                        rec in records if rec.lend_user == jerry])

    def test_resize_book_image(self, ctx, cli):
        from .fake.data import fake_book_img_path
        with ctx:
            with open(fake_book_img_path, 'rb') as f:
                rs = cli.post('/uploads', data={'h': 200, 'w': 200})
                img = BookThumbnail.query.order_by(BookThumbnail.create_at).desc().first()

    @property
    def jerry(self):
        return User.query.order_by(User.id).first()

    @property
    def users_book(self):
        return BookOfUser.query.order_by(BookOfUser.id).first()

    @property
    def branch(self):
        return Branch.query.order_by(Branch.id).first()

    @property
    def lend_records(self):
        records = UsersLendBook.query.all() or []
        if not records:
            rec = self.jerry.lend_book(branch=self.branch, book_copy=self.users_book)
            rec.state = BookLendState.WAIT
            rec.save()
            records.append(rec)
        return records





