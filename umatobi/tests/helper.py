# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import os, pickle

from umatobi.lib import *
from umatobi.simulator.sql import SchemaParser

def assert_queue(test_case, inspected_queue, expected_now, expected_info):
    st, info = pickle.loads(inspected_queue)
    test_case.assertEqual(st, expected_now)
    test_case.assertEqual(info, expected_info)

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
