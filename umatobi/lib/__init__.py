# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import json, time, os, threading, sched, configparser, re, shutil

import yaml
from umatobi.constants import *
from umatobi.log import *
from umatobi.simulator.sql import SchemaParser

def make_fixture(yaml_path, index):
    yaml_dir = os.path.dirname(yaml_path)
    schema_path, table_name, *components = load_yaml(yaml_path)[index]
    schema_path = os.path.join(yaml_dir, schema_path)
    schema_parser = SchemaParser(schema_path)
    fixture = tuple(schema_parser.parse_record(component, table_name) for component in components)
    return schema_parser, table_name, fixture

def inserts_fixture(db, yaml_path, index):
    schema_parser, table_name, fixture = make_fixture(yaml_path, index)
   #print('table_name =',table_name)
   #print('fixture =', fixture)
    if not table_name in db.get_table_names():
        db.create_table(table_name)
    listed_fixture = [tuple(fixture[0].keys())]
    listed_fixture.extend([tuple(x.values()) for x in fixture])
   #print('listed_fixture =', listed_fixture)

   #>>> L = [d.keys()]
   #>>> L
   #[dict_keys(['a', 'b', 'c'])]
   #>>> L.extend([x.values() for x in fix])
   #>>> L
   #[dict_keys(['a', 'b', 'c']), dict_values([1, 2, 3]), dict_values([4, 5, 6])]
    db.inserts(table_name, listed_fixture)
    db.commit()
    return schema_parser, table_name, fixture

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

class Polling(threading.Thread):

    @classmethod
    def sleep(cls, secs):
        logger.info(f'Polling.sleep(secs={secs})')
        time.sleep(secs)

    def __init__(self, polling_secs):
        threading.Thread.__init__(self)
        self.polling_secs = polling_secs
        self._sche = sched.scheduler(timefunc=time.time, delayfunc=Polling.sleep)
#       self._sche.enter(self.polling_secs, 1, self._polling, ()) # 犯人

    def polling(self):
        raise NotImplementedError()

    def is_continue(self):
        raise NotImplementedError()

    def _polling(self):
        if self.is_continue():
            self.polling()
            self._sche.enter(self.polling_secs, 1, self._polling, ())

    def run(self):
        self._sche.run()

if __name__ == '__main__':
    import umatobi
    print('umatobi.__path__ =', umatobi.__path__)
    import umatobi.lib
    print('umatobi.lib.__path__ =', umatobi.lib.__path__)
