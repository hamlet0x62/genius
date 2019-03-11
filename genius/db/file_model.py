# coding=utf-8
import os
import uuid
from genius.db import db
from genius.db import TimeMixin
from genius.util import get_file_md5, get_file_path
from werkzeug.utils import secure_filename
from sqlalchemy.ext.declarative import declared_attr
from genius.global_settings import file_url_fmt
from genius.db.mime import JPEG
from PIL import Image

from urllib import request

import cropresize2


class FileMixin(TimeMixin):
    __repr_attrs__ = ['id', 'mime_type', 'uid_filename', 'file_md5', 'name', 'url']

    mime_type = db.Column(db.String(128))
    uid_filename = db.Column(db.String(256), unique=True)
    name = db.Column(db.String(256))
    file_md5 = db.Column(db.String(256), unique=True)

    @declared_attr
    def id(cls):
        return db.Column(db.Integer, primary_key=True, index=True)

    def __init__(self, filename, mime_type, *args,
                 file_md5=None, uid=None, **kws):
        super(FileMixin, self).__init__(*args, **kws)
        self.name = filename
        self.mime_type = mime_type
        self.file_md5 = file_md5
        self.uid_filename = uid or self.get_uid_filename(filename)

    @classmethod
    def get_uid_filename(cls, filename):
        rs = filename.rsplit('.')
        ext = rs[-1] if len(rs) > 1 else ''
        assert ext
        ufilename = uuid.uuid4().hex + '.' + ext
        return ufilename

    def copy_from_this(self, other_cls):
        return other_cls(filename=self.name, mime_type=self.mime_type, file_md5=self.file_md5)

    @property
    def filepath(self):
        return get_file_path(self.uid_filename)

    @property
    def url(self):
        return file_url_fmt(self.uid_filename)

    @classmethod
    def create_from_file(cls, file):
        filename = secure_filename(file.filename)
        obj = cls(filename, file.mimetype)
        file.save(obj.filepath)

        with open(obj.filepath, 'rb') as f:
            obj.file_md5 = get_file_md5(f)
            record = cls.query.filter_by(file_md5=obj.file_md5).first()
        if record:
            os.remove(obj.filepath)
            return record
        obj.save()
        return obj


class UserImage(FileMixin):
    __repr_attrs__ = FileMixin.__repr_attrs__ + ['size']
    __refname__ = None

    @declared_attr
    def user_id(cls):
        return db.Column(db.ForeignKey('user.id'), index=True)

    @declared_attr
    def user(cls):
        if not cls.__refname__:
            raise AttributeError(f"__refname__ can not be {cls.__refname__}")
        return db.relationship('User', backref=cls.__refname__)


class UserAvator(UserImage, db.Model):
    __tablename__ = 'user_avator'
    __refname__ = "avators"


class BookImage(FileMixin):
    __repr_attrs__ = FileMixin.__repr_attrs__ + ['size']
    __refname__ = None

    @declared_attr
    def book_id(cls):
        return db.Column(db.ForeignKey('book.id'), index=True)

    @declared_attr
    def book(cls):
        refname = cls.__refname__ or cls.__name__.lower().replace('book', '') + 's'
        return db.relationship('Book', backref=f'{refname}')

    @property
    def size(self):
        with open(self.filepath, 'rb') as f:
            img = Image.open(f)
            return img.size

    def rsize(self, width, height):
        if (width, height) == self.size:
            return self

        with open(self.filepath, 'rb') as f:
            img = Image.open(f)
            result = cropresize2.crop_resize(img, (width, height), exact_size=False)
            result.save(self.filepath)
        return self

    @classmethod
    def retrieve_from_url(cls, url, book):
        _, filename = url.rsplit('/', 1)
        obj = cls(filename=filename, mime_type=JPEG)
        obj.book_id = book.id
        request.urlretrieve(url=url, filename=obj.filepath)
        obj.save()
        return obj


class BookThumbnail(BookImage, db.Model):
    __tablename__ = "book_thumb_nails"
    __refname__ = "thumbnails"


class BookDetailImage(BookImage, db.Model):
    __tablename__ = "book_detail_imgs"
    __refname__ = 'detail_imgs'


class UserBookImage(BookImage, db.Model):
    __tablename__ = "user_book_imgs"
    __refname__ = 'user_book_imgs'

    __repr_attrs__ = ['id', 'user_book']

    @declared_attr
    def user_book_id(self):
        return db.Column(db.ForeignKey('books_of_user.id'), index=True)

    @declared_attr
    def user_book(self):
        return db.relationship('BookOfUser', backref='imgs')
