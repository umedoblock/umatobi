import json

def dict_becomes_jbytes(d):
    js = json.dumps(d)
    jb = js.encode()
    return jb

def jbytes_becomes_dict(jb):
    js = jb.decode()
    d = json.loads(js)
    return d
