import json


def respond(body, http_status_code=200, headers=None):
    """creates response object for lambda proxy integrated objects

    Args:
        body (object): JSON serializable object
        http_status_code (int, optional): Status code, default 200
        headers (dict, optional): str->str dictionary of headers

    Returns:
        TYPE: dict
    """
    if headers is None:
        headers = {}

    return {
        "statusCode": http_status_code,
        "headers": headers,
        "body": json.dumps(body)
    }
    pass
