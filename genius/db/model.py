# coding: utf-8
from .mixin import TimeMixin, UUIDMixin
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.ext.associationproxy import association_proxy
import datetime
from .base import db
from .util_model import BookLendState, UserBookState, BranchBookState, UserBookDeprecation
from genius.global_setting import NO_IMG


class Book(TimeMixin, UUIDMixin, db.Model):
    __tablename__ = 'book'
    __repr_attrs__ = ["id", "name", "categories"]

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=True)
    isbn = db.Column(db.String(13))
    author = db.Column(db.String(25))
    categories = db.relationship('Category', secondary='books_of_categories', backref='books')

    @hybrid_property
    def all_copies(self):
        return self.books_of_users

    @property
    def cover_img_url(self):
        return self.thumbnails[0].url if len(self.thumbnails) > 0 else NO_IMG

    @property
    def detail_img_url(self):
        return self.detail_imgs[0].url if len(self.detail_imgs) > 0 else NO_IMG

    @classmethod
    def newly_books(cls):
        return cls.query.order_by(Book.create_at.desc()).limit(5).all()


t_books_of_categories = db.Table(
    'books_of_categories',
    db.Column('category_id', db.ForeignKey('category.id'), primary_key=True, nullable=False, index=True),
    db.Column('book_id', db.ForeignKey('book.id'), primary_key=True, nullable=False, index=True)
)


class BooksOfUser(TimeMixin, UUIDMixin, db.Model):
    __tablename__ = 'books_of_users'
    __repr_attrs__ = ['id', 'book', 'user']
    __table_args__ = (
        db.Index('AK_Identifier_1', 'book_id', 'user_id'),
    )
    id = db.Column(db.Integer, index=True, primary_key=True)

    book_id = db.Column(db.ForeignKey('book.id'), nullable=False, index=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False, index=True)
    book_state = db.Column(db.Enum(UserBookState), default=UserBookState.WAIT)
    deprecation = db.Column(db.SmallInteger, default=UserBookDeprecation.ERROR)

    return_date = association_proxy('lend_records', 'return_date')

    book = db.relationship('Book', primaryjoin='BooksOfUser.book_id == Book.id', backref='books_of_users')
    user = db.relationship('User', primaryjoin='BooksOfUser.user_id == User.id', backref='books_of_users')


class Branch(db.Model, TimeMixin):
    __tablename__ = 'branch'

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.ForeignKey('school.id'), index=True)
    branch_addr = db.Column(db.String(100))
    branch_tel = db.Column(db.String(11))
    branch_name = db.Column(db.String(20), unique=True)

    school = db.relationship('School', primaryjoin='Branch.school_id == School.id', backref='branches')


class Category(TimeMixin, db.Model):
    __tablename__ = 'category'
    __repr_attrs__ = ['id', 'category_name']

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(20), nullable=False, unique=True)


class Role(TimeMixin, db.Model):
    __tablename__ = 'role'
    __repr_attrs__ = ['id', 'role_name', 'lend_limitation']
    id = db.Column(db.Integer, primary_key=True)
    permission = db.Column(db.Integer, default=0x000f)
    role_name = db.Column(db.String(10))
    limit_type_id = db.Column(db.ForeignKey('lend_limitation.id'))

    @hybrid_property
    def lend_limitation(self):
        return LendLimitation.query.get(self.limit_type_id)


class LendLimitation(TimeMixin, db.Model):
    ___tablename__ = 'lend_limitation'
    __repr_attrs__ = ('id', 'limit_days', 'limit_nums')

    id = db.Column(db.Integer, primary_key=True)
    limit_days = db.Column(db.Integer)
    limit_nums = db.Column(db.Integer)


t_roles_of_users = db.Table(
    'roles_of_users',
    db.Column('user_id', db.ForeignKey('user.id'), primary_key=True, nullable=False),
    db.Column('role_id', db.ForeignKey('role.id'), primary_key=True, nullable=False, index=True)
)


class School(TimeMixin, db.Model):
    __tablename__ = 'school'
    __repr_attrs__ = ['id', 'school_name', 'create_at', 'user_nums']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_name = db.Column(db.String(15), nullable=False, unique=True)
    school_addr = db.Column(db.String(100))
    school_tel = db.Column(db.String(11))

    @hybrid_property
    def user_nums(self):
        return len(self.users)


class User(TimeMixin, db.Model):
    __tablename__ = 'user'
    __repr_attrs__ = ['id', 'username', 'borrowed_book_nums']

    username = db.Column(db.String(25), unique=True, index=True)
    password = db.Column(db.String(255))
    nickname = db.Column(db.String(20))
    email = db.Column(db.String(30), nullable=False, unique=True)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_id = db.Column(db.ForeignKey('school.id'), index=True)
    role_id = db.Column(db.ForeignKey('role.id'))
    balance = db.Column(db.Numeric(9, 2), default=0)

    school = db.relationship('School', primaryjoin='User.school_id == School.id', backref='users')

    lend_limit = association_proxy('role', 'lend_limitation')
    role = db.relationship('Role', backref="users", lazy='select')

    @hybrid_property
    def borrowed_book_nums(self):
        return len(self.borrowed_records)

    @hybrid_method
    def lend_book(self, book_copy: BooksOfUser, branch: Branch):
        if self.lend_limit.limit_nums < self.borrowed_book_nums or book_copy in self.borrowed_records :
            return None

        return UsersLendBook.create_with_uuid(lend_user_id=self.id,
                                              lend_id=book_copy.id, branch_id=branch.id,
                                              days_limit=self.lend_limit.limit_days)

    @hybrid_method
    def return_books(self, lend_records):
        """

        :param lend_records: UsersLendBook
        :return returned lend_records else False
        """
        valid = all([rec in self.borrowed_records and rec.state == BookLendState.LENDING
                     for rec in lend_records])
        if valid:
            return _run_map(map(lambda rec:rec._return_this(), lend_records))
        else:
            return False

    @hybrid_method
    def ensure_lending(self, lend_records):
        """

        :param lend_records: UsersLendBook
        :return: UsersLendBook
        """

        valid = all([rec in self.borrowed_records for rec in lend_records])
        return _run_map(map(lambda r: r._lender_ensure_this(), lend_records)) if valid else None

    def __init__(self, *args, **kws):
        for k, v in kws.items():
            setattr(self, k, v)

    @hybrid_method
    def post_book(self, book: Book):
        return BooksOfUser.create_or_get(book_id=book.id, user_id=self.id)


class UsersLendBook(UUIDMixin, TimeMixin, db.Model):
    __tablename__ = 'users_lend_books'
    __repr_attrs__ = ['id', 'lend_user', 'days_limit', 'branch', 'state']

    id = db.Column(db.Integer, primary_key=True, index=True)
    lend_user_id = db.Column(db.ForeignKey('user.id'), index=True)
    lend_id = db.Column(db.ForeignKey('books_of_users.id'))
    days_limit = db.Column(db.Integer)
    branch_id = db.Column(db.ForeignKey("branch.id"), index=True)
    left_date = db.Column(db.Date)
    state = db.Column(db.Enum(BookLendState),
                      default=BookLendState.WAIT)  # default state 0 represents `haven't been processed yet `

    book_of_user = db.relationship('BooksOfUser',
                                   primaryjoin='UsersLendBook.lend_id == BooksOfUser.id',
                                   backref='lend_records')
    lend_user = db.relationship('User', primaryjoin='UsersLendBook.lend_user_id == User.id',
                                backref='borrowed_records')
    branch = db.relationship('Branch')

    @hybrid_property
    def date_exceeded(self):
        return self.left_date + datetime.timedelta(days=self.days_limit) > datetime.datetime.now()

    @hybrid_method
    def _return_this(self):
        self.state = BookLendState.BACKING
        return self

    @hybrid_method
    def _lender_ensure_this(self):
        self.state = BookLendState.LENDING
        return self.left_date + datetime.timedelta(days=self.days_limit)

    @hybrid_property
    def return_date(self):
        return


def _run_map(map_obj):
    return list(map_obj)