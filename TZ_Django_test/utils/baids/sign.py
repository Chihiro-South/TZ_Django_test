from itsdangerous import TimedJSONWebSignatureSerializer as s

from TZ_Django_test.settings.dev import SECRET_KEY


def dumps(dicts, expires):
    signs = s(SECRET_KEY, expires_in=expires)
    js_str = signs.dumps(dicts).decode()

    return js_str

def loads(json_str, expires):
    signs = s(SECRET_KEY, expires_in=expires)
    try:
        js = signs.loads(json_str)
    except:
        return None
    else:
        return js