# coding: utf-8

from sqlalchemy import func, select
from sqlalchemy.orm import column_property, query_expression, with_expression
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from flask_login import UserMixin

from .mixin import TimeMixin, UUIDMixin
from .base import db

from .util_model import BookLendState, UserBookState, BranchBookState, UserBookDeprecation

from genius.global_settings import NO_IMG
from genius.db.util_model import user_address
import genius.db.utils as db_helper

import datetime


t_books_of_categories = db.Table(
    'books_of_categories',
    db.Column('category_id', db.ForeignKey('category.id'), primary_key=True, nullable=False, index=True),
    db.Column('book_id', db.ForeignKey('book.id'), primary_key=True, nullable=False, index=True)
)


class Book(TimeMixin, UUIDMixin, db.Model):
    __tablename__ = 'book'
    __repr_attrs__ = ["id", "name", "categories", "collected_times"]

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50))
    other_name = db.Column(db.String(50))
    isbn = db.Column(db.String(13))

    pub_date = db.Column(db.String(10))
    publisher = db.Column(db.String(20))
    douban_id = db.Column(db.Integer)

    authors = association_proxy('_authors', 'name')
    copies = db.relationship('BookOfUser')

    categories = db.relationship('Category', secondary='books_of_categories', backref='books')
    expr = query_expression()

    @declared_attr
    def _authors(cls):
        class Author(db.Model):
            __tablename__ = f"{cls.__tablename__}_author"
            id = db.Column(db.Integer, autoincrement=True, primary_key=True)
            name = db.Column(db.String(50))
            parent_id = db.Column(db.ForeignKey(f'{cls.__tablename__}.id'), nullable=False)

            def __init__(self, name):
                self.name = name

        return db.relationship(Author)

    @hybrid_property
    def all_copies(self):
        return self.copies

    @hybrid_property
    def collected_times(self):
        return len(self.collected_users)

    @collected_times.expression
    def copy_nums(cls):
        return cls.collected_users.count()

    @hybrid_property
    def cover_img_url(self):
        new_covers = sorted(self.thumbnails, key=lambda x: x.create_at, reverse=True)
        return new_covers[0].url if new_covers else NO_IMG

    @property
    def detail_img_url(self):
        return self.cover_img_url

    @classmethod
    def newly_books(cls):
        return cls.query.order_by(Book.create_at.desc()).limit(5).all()

    @classmethod
    def most_copies(cls, num=5):
        count_expr = func.count(cls.copies)

        query_string = cls.query.options(with_expression(cls.expr, count_expr))\
            .group_by(Book.id).order_by(count_expr.desc()).limit(num)

        return query_string.all()

    @classmethod
    def most_collected(cls):
        return cls.query.order_by(cls.collected_times, 'desc').all()


class BookOfUser(TimeMixin, UUIDMixin, db.Model):
    __tablename__ = 'books_of_user'
    __repr_attrs__ = ['id', 'book', 'user', 'deprecation',
                      'book_state', 'description', 'avg_rate',
                      'rate_num', 'img_urls', 'borrow_times']
    __table_args__ = (
        db.Index('AK_Identifier_1', 'book_id', 'user_id'),
    )
    id = db.Column(db.Integer, index=True, primary_key=True)

    book_id = db.Column(db.ForeignKey('book.id'), nullable=False, index=True)
    user_id = db.Column(db.ForeignKey('user.id'), nullable=False, index=True)
    book_state = db.Column(db.Enum(UserBookState), default=UserBookState.WAIT)
    deprecation = db.Column(db.SmallInteger, default=UserBookDeprecation.ERROR)
    description = db.Column(db.String(50))

    # total_rate stores an integer as large as 10x to actual total float type scores
    total_rate = db.Column(db.Integer, default=0)

    rate_num = db.Column(db.Integer, default=0)
    address_id = db.Column(db.ForeignKey('user_address.id'))

    return_date = association_proxy('lend_records', 'return_date')

    address_val = association_proxy('address', 'value')

    book = db.relationship('Book', primaryjoin='BookOfUser.book_id == Book.id')
    user = db.relationship('User', primaryjoin='BookOfUser.user_id == User.id', backref='books_of_user')

    @hybrid_property
    def is_lending(self):
        return self.book_state == UserBookState.OUT

    @hybrid_property
    def blocking(self):
        return self.book_state == UserBookState.IN_STOCK

    @hybrid_property
    def asleep(self):
        return self.book_state == UserBookState.WAIT

    @hybrid_property
    def avg_rate(self):
        return (self.total_rate / 10) / self.rate_num if self.rate_num > 0 else None

    @hybrid_property
    def borrow_times(self):
        return len(self.lend_records)

    @property
    def img_urls(self):
        return [img.url for img in self.imgs]



class Branch(db.Model, TimeMixin):
    __tablename__ = 'branch'

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.ForeignKey('school.id'), index=True)
    addr = db.Column(db.String(100))
    tel = db.Column(db.String(11))
    name = db.Column(db.String(20), unique=True)

    school = db.relationship('School', primaryjoin='Branch.school_id == School.id', backref='branches')


class Category(TimeMixin, db.Model):
    __tablename__ = 'category'
    __repr_attrs__ = ['id', 'category_name']

    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(20), nullable=False, unique=True)


class Role(TimeMixin, db.Model):
    __tablename__ = 'role'
    __repr_attrs__ = ['id', 'description', 'lend_limitation']
    id = db.Column(db.Integer, primary_key=True)
    permission = db.Column(db.Integer, default=0x000f)
    description = db.Column(db.String(20))
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
    __repr_attrs__ = ['id', 'name', 'create_at', 'user_nums']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(15), nullable=False, unique=True)
    addr = db.Column(db.String(100))
    tel = db.Column(db.String(11))

    @hybrid_property
    def user_nums(self):
        return len(self.users)


class CommonAddress(TimeMixin, db.Model):
    __tablename__ = 'common_address'
    __repr_attrs__ = ['id', 'code']

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10))


class UserAddress(TimeMixin, db.Model):
    __tablename__ = 'user_address'

    __repr_attrs__ = ['id', 'common_addr_code', 'detail', 'label']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
    detail = db.Column(db.String(50))
    label = db.Column(db.String(10))
    parent_id = db.Column(db.ForeignKey('user.id'))
    common_addr_id = db.Column(db.ForeignKey('common_address.id'))

    common_addr_code = association_proxy('common_addr', 'code')
    common_addr = db.relationship('CommonAddress', backref='user_address_list')
    book_of_users = db.relationship('BookOfUser', backref='address')
    user = db.relationship('User', backref='address')

    @hybrid_property
    def item(self):
        """
        :return: a namedtuple
        """
        return user_address(label=self.label, common_addr=self.common_addr,
                            detail=self.detail)

    def __init__(self, *args, item=None, **kws):
        if item:
            self.label = item.label
            self.common_addr = item.common_addr
            self.detail = item.detail
        db.Model.__init__(self, **kws)


class User(TimeMixin, db.Model, UserMixin):
    __tablename__ = 'user'
    __repr_attrs__ = ['id', 'username', 'borrowed_book_nums', 'role',
                      'nickname', 'school', 'email', 'avator_url', 'address']

    username = db.Column(db.String(25), unique=True, index=True)
    password = db.Column(db.String(255))
    nickname = db.Column(db.String(20))
    email = db.Column(db.String(30), nullable=False, unique=True)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    school_id = db.Column(db.ForeignKey('school.id'), index=True)
    role_id = db.Column(db.ForeignKey('role.id'))
    balance = db.Column(db.Numeric(9, 2), default=0)
    active = db.Column(db.Boolean)
    primary_address_id = db.Column(db.Integer)
    school = db.relationship('School', primaryjoin='User.school_id == School.id', backref='users')

    address_items = association_proxy('address', 'item', creator=lambda val: UserAddress(item=val))

    role = db.relationship('Role', backref="users", lazy='select')

    def has_collected(self, book):
        return True if any([collection.book_id == book.id for collection in self.collections]) else False

    @hybrid_property
    def borrowed_book_nums(self):
        return len(self.borrowed_records)

    @hybrid_property
    def lend_limit(self):
        return self.role.lend_limitation

    @hybrid_property
    def avator_url(self):
        return self.avators[0].url if self.avators else NO_IMG

    def lend_book(self, book_copy: BookOfUser, branch: Branch):
        if self.lend_limit.limit_nums < self.borrowed_book_nums or book_copy in list(self.borrowed_records):
            return None

        return UsersLendBook.create_with_uuid(lend_user_id=self.id,
                                              userbook_id=book_copy.id, branch_id=branch.id,
                                              days_limit=self.lend_limit.limit_days)

    def return_books(self, lend_records):
        """

        :param lend_records: UsersLendBook
        :return returned lend_records if lend_records all valid else None
        """
        valid = all([rec in self.borrowed_records and rec.state == BookLendState.LENDING
                     for rec in lend_records])
        if valid:
            rst = _run_map(map(lambda rec: rec._return_this(), lend_records))
            db_helper.save_all(rst)
        else:
            return None

    def ensure_lending(self, lend_records):
        """

        :param lend_records: UsersLendBook
        :return: UsersLendBook
        """

        valid = all([rec in self.borrowed_records for rec in lend_records])
        rst = _run_map(map(lambda r: r._lender_ensure_this(), lend_records)) if valid else None
        if rst:
            db_helper.save_all(rst)

    def __init__(self, *args, **kws):
        for k, v in kws.items():
            setattr(self, k, v)

    def post_book(self, book: Book, address_id):
        userbook = BookOfUser(book_id=book.id, user_id=self.id)
        userbook.address_id = address_id
        userbook.save()
        return userbook


class UserCollection(TimeMixin, db.Model):
    __tablename__ = 'user_collection'
    __repr_attrs__ = ['id', 'book', 'create_at']
    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id'),
    )

    id = db.Column(db.Integer, primary_key=True, index=True)
    book_id = db.Column(db.ForeignKey('book.id'), index=True)
    user_id = db.Column(db.ForeignKey('user.id'), index=True)

    book = db.relationship('Book', backref="collected_users")
    user = db.relationship('User', backref='collections')


class UsersLendBook(UUIDMixin, TimeMixin, db.Model):
    __tablename__ = 'users_lend_book'
    __repr_attrs__ = ['id', '_uuid', 'branch', 'state', 'book', 'own_user', 'return_date', 'left_date']

    id = db.Column(db.Integer, primary_key=True, index=True)
    lend_user_id = db.Column(db.ForeignKey('user.id'), index=True)
    userbook_id = db.Column(db.ForeignKey('books_of_user.id'))
    days_limit = db.Column(db.Integer)
    branch_id = db.Column(db.ForeignKey("branch.id"), index=True)
    left_date = db.Column(db.DateTime)
    state = db.Column(db.Enum(BookLendState),
                      default=BookLendState.WAIT)  # default state 0 represents `haven't been processed yet `

    book_of_user = db.relationship('BookOfUser',
                                   primaryjoin='UsersLendBook.userbook_id == BookOfUser.id',
                                   backref='lend_records')
    lend_user = db.relationship('User', primaryjoin='UsersLendBook.lend_user_id == User.id',
                                backref='borrowed_records')
    branch = db.relationship('Branch')
    address_id = db.Column(db.ForeignKey('user_address.id'))

    book = association_proxy('book_of_user', 'book')
    own_user = association_proxy('book_of_user', 'user')

    @hybrid_property
    def date_exceeded(self):
        return self.left_date + datetime.timedelta(days=self.days_limit) > datetime.datetime.now()

    def _return_this(self):
        self.state = BookLendState.BACKING
        self.book_of_user.book_state = UserBookState.BACKING
        return self

    def _lender_ensure_this(self):
        self.state = BookLendState.LENDING
        self.book_of_user.book_state = UserBookState.OUT
        self.left_date = datetime.datetime.now()

        return self

    @hybrid_property
    def return_date(self):
        return self.left_date + datetime.timedelta(days=self.days_limit)

    @hybrid_property
    def is_borrowing(self):
        return self.state == BookLendState.LENDING


def _run_map(map_obj):
    return list(map_obj)
