# coding=utf-8

from flask import url_for

from collections import namedtuple

from functools import partial

link_item = namedtuple('LinkItem', ['label', 'view_func', 'link_name_prop'])
user_link_item = partial(link_item, link_name_prop='nickname')
book_link_item = partial(link_item, link_name_prop='name')

filter_item = namedtuple('FilterItem', ['label', 'method'])

popover_item = namedtuple('PopoverItem', ['label', 'cell_label', 'content_prop'])
description_popover_item = partial(popover_item, label=u'描述', cell_label='详情')

table_header_dict = {
    'id': u'ID',
    'state': u'状态',
    'lend_user': u'借阅用户ID',
    'days_limit': u'借阅期限',
    'return_date': u'归还日期',
    'left_date': u'借阅日期',
    'branch': u'线下中介点',
    '_uuid': u'编号',
    'deprecation': u'折旧率',
    'description': description_popover_item(content_prop='description'),
    'book_state': u'状态',
    'user': user_link_item(u'用户', 'user.profile'),
    'own_user': user_link_item(u'归属用户', 'user.profile'),
    'book': u'书籍'
}

user_profile_marshal = lambda user: {
    'id': user.id,
    'nickname': user.nickname,
    'profile_url': url_for('user.profile', user_id=user.id)
}

fmt_date = lambda date_: date_.strftime('%Y-%m-%d')

userlendbook_schema = {
    'book': lambda x: x.name,
    'branch': lambda x: x.name,
    'return_date': lambda return_date: fmt_date(return_date),
    'left_date': lambda left_date: fmt_date(left_date),
    'own_user': lambda x: {
        'id': x.id,
        'nickname': x.nickname
    }

}

bookofuser_schema = {
    'book': lambda x: x.name,
    'deprecation': lambda x: u'异常' if x <= 0 else f'{x/100}',
    'user': user_profile_marshal,
    'description': lambda x: x or u'暂无描述'
}

user_schema = {
    'school': lambda x: x.name,
    'role': lambda role: role.description,
    'address': lambda address_list: [item.to_dict() for item in address_list]
}

user_collection_schema = {
    'book': lambda x: {
        'name': x.name,
        'id': x.id
    },
    'create_at': lambda x: fmt_date(x),
    'user': lambda x: {
        'nickname': x.nickname,
    },
}

user_collection_header_patch = {
    'create_at': '收藏于',
    'book': book_link_item('书籍', 'book.detail')
}