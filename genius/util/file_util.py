import os
from genius.global_setting import UPLOAD_DIR
import hashlib


def get_file_path(filename):
    return os.path.join(UPLOAD_DIR, filename)


def get_file_md5(file, chunk_size=1024*4):
    _md5 = hashlib.md5()

    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            break
        _md5.update(chunk)
    return _md5.hexdigest()