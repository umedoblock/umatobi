# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

import os, re, shutil
from datetime import datetime as datetime2

from umatobi.constants import *
from umatobi.simulator.sql import SchemaParser
from umatobi.log import *

class SimulationTime(object):
    Y15S_FORMAT='%Y-%m-%dT%H%M%S'

    @classmethod
    def now(cls):
        return datetime2.now()

    @classmethod
    def iso8601_to_time(cls, iso8601format):
        start_up_orig = datetime2.fromisoformat(iso8601format)
        return SimulationTime(start_up_orig)

    @classmethod
    def time_to_iso8601(cls, simulation_time):
      # >>> datetime2.isoformat(now)
      # '2019-08-27T02:43:20.708976'
        return datetime2.isoformat(simulation_time.start_up_orig)

    @classmethod
    def y15s_to_time(cls, y15s):
        start_up_orig = \
            datetime2.strptime(y15s, SimulationTime.Y15S_FORMAT)
        return SimulationTime(start_up_orig)

    @classmethod
    def time_to_y15s(cls, simulation_time):
        start_up_orig = simulation_time.start_up_orig
        return start_up_orig.strftime(SimulationTime.Y15S_FORMAT)

    def __init__(self, start_up_orig=None):
        if not start_up_orig:
            self.start_up_orig = SimulationTime.now()
        else:
            self.start_up_orig = start_up_orig

    def __str__(self):
        return self.get_iso8601()

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.start_up_orig == other.start_up_orig

    def get_iso8601(self):
        return SimulationTime.time_to_iso8601(self)

    def get_y15s(self):
        return SimulationTime.time_to_y15s(self)

    def passed_seconds(self, now=None):
        if not now:
            now = SimulationTime.now()
        return (now - self.start_up_orig).total_seconds()

    def passed_ms(self, now=None):
        '''simulation 開始から現在までに経過したmilli秒数。'''

        if not now:
            now = SimulationTime.now()
        # relativeCreated の時間単位がmsのため、
        # elapsed_time()もms単位となるようにする。
        return int(self.passed_seconds(now) * 1000)

# def isoformat_to_start_up_orig(isoformat):
#   # >>> datetime2.fromisoformat('2019-08-27T02:43:20.708976')
#   # datetime2(2019, 8, 27, 2, 43, 20, 708976)
#     return datetime2.fromisoformat(isoformat)

# Y15S_FORMAT='%Y-%m-%dT%H%M%S'
# def y15sformat_time(t):
#     "'return time format '2012-11-02T232227'"
#     return t.strftime(Y15S_FORMAT)
#
# def current_y15sformat_time():
#     now = datetime_now()
#     return y15sformat_time(now)

# def y15sformat_parse(s):
#     return datetime2.strptime(s, Y15S_FORMAT)

class PathMaker(object):

    def __eq__(self, other):
        return self.simulation_time == other.simulation_time

    def __init__(self, simulation_time_or_start_up_orig=None):
        st_or_suo = simulation_time_or_start_up_orig
        if isinstance(st_or_suo, SimulationTime):
            self.simulation_time = st_or_suo
        else:
            self.simulation_time = SimulationTime(st_or_suo)

    def get_client_db_path(self, client_id):
        client_n_db = re.sub(ATAT_N, str(client_id), CLIENT_N_DB)
        return os.path.join(self.get_simulation_dir_path(), client_n_db)

    def get_simulation_dir_path(self):
        simulation_dir_path = re.sub(ATAT_SIMULATION_TIME,
                                     self.simulation_time.get_y15s(),
                                     UMATOBI_SIMULATION_DIR_PATH)
        return simulation_dir_path

    def get_simulation_db_path(self):
        simulation_db_path = os.path.join(self.get_simulation_dir_path(),
                                          SIMULATION_DB)
        return simulation_db_path

    def get_simulation_schema_path(self):
        simulation_schema_path = os.path.join(self.get_simulation_dir_path(),
                                              SIMULATION_SCHEMA)

        return simulation_schema_path

    def get_module_path(self):
        return UMATOBI_MODULE_PATH

    def set_simulation_schema(self):
        simulation_schema_path = self.get_simulation_schema_path()

        if not os.path.isfile(simulation_schema_path):
            self.make_simulation_dir()
            logger.info(f"shutil.copyfile(SIMULATION_SCHEMA_PATH={SIMULATION_SCHEMA_PATH}, simulation_schema_path={simulation_schema_path})")
            shutil.copyfile(SIMULATION_SCHEMA_PATH, simulation_schema_path)

        return simulation_schema_path

    def get_master_palm_txt_path(self):
        return os.path.join(self.get_simulation_dir_path(), MASTER_PALM_TXT)

    def make_simulation_dir(self, simulation_dir_path=None):
        if not simulation_dir_path:
            simulation_dir_path = self.get_simulation_dir_path()

        if not os.path.isdir(simulation_dir_path):
            logger.info(f"os.makedirs('{simulation_dir_path}')")
            os.makedirs(simulation_dir_path, exist_ok=True)

        return simulation_dir_path
