# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import json, yaml

def validate_kwargs(st_barrier, kwargs):
    if st_barrier != kwargs.keys():
        st_unknown = kwargs.keys() - st_barrier
        st_must = st_barrier - kwargs.keys()
        message = ('unmatched st_barrier and kwargs.keys().\n'
                   'unknown keys are {},\n'
                   'must keys are {}').format(st_unknown, st_must)
        raise RuntimeError(message)

def bytes2dict(b):
    j = b.decode('utf-8')
    return json2dict(j)

def dict2bytes(d):
    j = dict2json(d)
    return j.encode('utf-8')

def dict2json(d):
    j = json.dumps(d)
    return j + '\n'

def json2dict(j):
    d = json.loads(j)
    return d

def tell_shutdown_time():
    shutdown_time = datetime_now()
    return shutdown_time

def load_yaml(yaml_path):
    with open(yaml_path) as f:
        y = yaml.load(f, Loader=yaml.SafeLoader)
    return y

def allot_numbers(total, an_allotment):
    # assign number equality
    if total <= an_allotment:
        heads = 1
        assigned_num = total
        last = total
    else:
        div, mod = divmod(total, an_allotment)
        if mod == 0:
            mod = an_allotment
        else:
            div += 1
        heads = div
        assigned_num = an_allotment
        last = mod

    return heads, assigned_num, last

def make_growing_dict(id_, et, pickle):

    growing = {
        'id': id_,
        'elapsed_time': et,
        'pickle': pickle,
    }

    return growing

if __name__ == '__main__':
    import umatobi
    print('umatobi.__path__ =', umatobi.__path__)
    import umatobi.lib
    print('umatobi.lib.__path__ =', umatobi.lib.__path__)
