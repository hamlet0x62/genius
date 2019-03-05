from flask import jsonify

from werkzeug.http import HTTP_STATUS_CODES


def api_abort(code, message=None):
    response = jsonify(code=code, message=message or HTTP_STATUS_CODES.get(code))
    response.status_code = code

    return response
