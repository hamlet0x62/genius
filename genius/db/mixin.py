from .base import db

from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr


import uuid
import enum


class BaseMixin:
    __table_args__ = {'mysql_charset': 'utf8mb4'}
    __repr_attrs__ = ['id']

    @classmethod
    def create_or_get(cls, **kwargs):
        session = db.session
        if 'id' in kwargs:
            obj = session.query(cls).get(kwargs['id'])
            if obj:
                return obj
        obj = cls(**kwargs)
        session.add(obj)
        session.commit()

        return obj

    @classmethod
    def save_all(cls, models):
        db.session.add_all(models)
        db.session.commit()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<' + type(self).__name__ + ' ' +\
               ' '.join([f"{attr}: {getattr(self, attr)}" for attr in self.__repr_attrs__]) \
               + '>'

    def __eq__(self, other):
        if getattr(self, 'id') and getattr(other, 'id'):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def to_dict(self, schema=None):
        schema = schema or {}
        rv = {}
        for attr in self.__repr_attrs__:
            item = getattr(self, attr)
            marshal_attr = schema.get(attr, None)
            item = item if not marshal_attr else marshal_attr(item) \
                if callable(marshal_attr) else getattr(item, marshal_attr)
            rv[attr] = item.id if isinstance(item, BaseMixin) else item.name if isinstance(item, enum.Enum) else item

        return rv

    def delete(self):
        session = db.session
        try:
            session.delete(self)
            session.commit()
        except:
            session.rollback()


class TimeMixin(BaseMixin):
    create_at = db.Column(db.DATETIME, default=func.now())
    update_at = db.Column(db.DATETIME, onupdate=func.now())


class UUIDMixin(BaseMixin):
    _uuid = db.Column(db.String(48), unique=True, index=True)

    @classmethod
    def create_with_uuid(cls, **kwargs):
        """
        return an obj with _uuid property
        and save it if kwargs is not empty else
        return a transient object only with _uuid property
        :param kwargs:
        :return:
        """
        session = db.session
        if "_uuid" in kwargs:
            obj = session.query(cls).get(_uuid=kwargs["_uuid"])
            if obj:
                return obj
            if kwargs:
                obj = cls(**kwargs)
                session.add(obj)
                session.commit()
        else:
            obj = cls(_uuid=uuid.uuid4().hex, **kwargs)
            if kwargs:
                session.add(obj)
                session.commit()
        return obj

