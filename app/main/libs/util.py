def camelcase(s):
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


def get_error(status_code, message, **kwargs):
    return {"errors": [
        {
            "status": status_code,
            "detail": message,
            **kwargs
        }
    ]}, status_code
