import io


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


def create_image_file(filename, content_type):
    file = io.BytesIO(b"abcdef")
    file.filename = filename
    file.content_type = content_type
    return file