class FormNotMatchException(Exception):
    def __init__(self, msg, *args, **kws):
        Exception.__init__(self, msg, *args, **kws)
