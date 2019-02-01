from collections import namedtuple
from functools import partial

BASIC_OPs = ['edit', 'remove']

mv_tuple = ('method', 'value')
OrderOpNeed = namedtuple("order_operation", mv_tuple) # Order operation needs


BookNeed = namedtuple('book_operation', mv_tuple)

