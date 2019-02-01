import enum


class BookLendState(enum.Enum):
    WAIT = 0
    INSTOCK = 1
    LENDING = 2
    BACKING = 3
    OUT_OF_DATE = 4


class UserBookState(enum.Enum):
    WAIT = 0
    IN_STOCK = 1
    OUT = 2
    BACKING = 3


class BranchBookState(enum.Enum):
    WAITING = 1
    OUT_OF_DATE = 2
    LEAVE = 3


class UserBookDeprecation:
    """
    static variable describe Books' deprecation rate
    rate <= BAD means bad deprecation rate
    rate <= NORMAL means normal deprecation rate
    ...
    """
    ERROR = -1
    BAD = 50 * 100
    NORMAL = 70 * 100
    GOOD = 90 * 100
    PERFECT = 95 * 100
