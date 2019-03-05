from flask import request
from flask_principal import Principal, Identity, Permission, RoleNeed,\
    UserNeed, identity_loaded, identity_changed
from flask_login import current_user

from genius.global_settings import USER_ROLE, OL_OPERATION_ROLE, BRANCH_OPERATION_ROlE
from genius.db.model import BookOfUser
from functools import partial
from collections import namedtuple


def make_meta_need(need_name):
    return namedtuple(need_name, ['method', 'value'])


# needs for managing posted books
BookManageNeed = namedtuple('BookManageNeed', ['method', 'value'])
UserEditBookNeed = partial(BookManageNeed, 'edit')

ReturnBookNeed = partial(BookManageNeed, 'book_id')

# needs for managing borrowed records
BorrowRecNeed = make_meta_need('BorrowNeed')
ReviewRecordNeed = partial(BorrowRecNeed, 'made')


principal = Principal()


@identity_loaded.connect
def load_needs(sender, identity: Identity):
    identity.user = current_user

    if getattr(current_user, 'id', None):
        identity.provides.add(UserNeed(current_user.id))
        identity.provides.add(RoleNeed(USER_ROLE))


class UserBookPermission(Permission):
    url_param_key = 'user_book_id'

    @property
    def user_book_id(self):
        return request.view_args.get(self.url_param_key, None)


class EditUserBookPermission(UserBookPermission):
    def allows(self, identity):
        if self.user_book_id:
            user_book = BookOfUser.query.get_or_404(self.user_book_id)
            rst = user_book.user_id == identity.user_id
            return rst


# role permissions
user_role_permission = Permission(RoleNeed(USER_ROLE))
ol_operator_role_permission = Permission(RoleNeed(OL_OPERATION_ROLE))
branch_operator_role_permission = Permission(RoleNeed(BRANCH_OPERATION_ROlE))


edit_userbook_permission = EditUserBookPermission()
