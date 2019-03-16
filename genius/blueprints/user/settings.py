from collections import namedtuple
from functools import partial

aside_nav_tab = namedtuple('aside_tab', ['name', 'view_func_name', 'child_tabs'])

aside_parent_tab = partial(aside_nav_tab, view_func_name=None)
aside_no_child_tab = partial(aside_nav_tab, child_tabs=None)

# user_bp's view  TODO
tabs = [
    aside_parent_tab('个人信息', child_tabs=[
                    aside_no_child_tab('我的信息', 'space'),
                    aside_no_child_tab('修改个人信息', 'update_profile')
    ]),
    aside_parent_tab('借阅记录',
                     child_tabs=[
                         aside_no_child_tab('借阅历史', 'borrow_history'),
                         aside_no_child_tab('正在借阅', 'borrowing'),
                     ]),
    aside_parent_tab('我的精灵',
                     child_tabs=[
                         aside_no_child_tab('在异乡', 'lending_genius'),
                         aside_no_child_tab('在家', 'blocking_genius'),
                         aside_no_child_tab('还未醒', 'asleep_genius'),
                         aside_no_child_tab('新的精灵', 'new_genius')
                     ]),
    aside_no_child_tab('收藏夹',
                       'collection'
                       ),
]
