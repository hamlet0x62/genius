# coding=utf-8
import os
from collections import namedtuple

from .config import SSL_ENABLED
from .deploy_config import DEPLOY_HOST

HERE = os.path.dirname(__file__)
IS_DEPLOY = os.environ.get('GENIUS_MODE') == 'deploy'
STATIC_FILE_DIR = os.path.join(HERE, 'static')
UPLOAD_DIR = os.path.join(STATIC_FILE_DIR, 'uploads')
STATIC_FILE_HOST = '127.0.0.1:5000/i' if not IS_DEPLOY else DEPLOY_HOST

protocol = 'https' if SSL_ENABLED else 'http'

file_url_fmt = lambda filename: f"{protocol}://{STATIC_FILE_HOST}/{filename}"
NO_IMG = file_url_fmt('no_img.jpeg')

tab = namedtuple('Tab', ['tagname', 'bp_name', 'subtabs', 'view_func_name'])
subtab = namedtuple('SubTab', ['tagname', 'view_func_name'])

index_tab = tab(u'首页', 'home', None, 'send_home')
book_list_tab = tab(u'书单', 'book', [subtab(u'全部书籍', 'all_books')], None)

NAV_TABS = (index_tab, book_list_tab)

# Role settings
USER_ROLE, OL_OPERATION_ROLE, BRANCH_OPERATION_ROlE = 'USER', 'Ol_OPERATOR', 'OFF_LINE_WORKER'
