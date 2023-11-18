"""Various utilities (logger, time benchmark, args dump, numerical and stats info)"""


def is_base64(sb):
    import base64

    try:
        if isinstance(sb, str):
            # If there's any unicode here, an exception will be thrown and the function will return false
            sb_bytes = bytes(sb, 'ascii')
        elif isinstance(sb, bytes):
            sb_bytes = sb
        else:
            raise ValueError("Argument must be string or bytes")
        return base64.b64encode(base64.b64decode(sb_bytes, validate=True)) == sb_bytes
    except ValueError:
        return False


def base64_decode(s):
    import base64

    if isinstance(s, str) and is_base64(s):
        return base64.b64decode(s, validate=True).decode("utf-8")

    return s
