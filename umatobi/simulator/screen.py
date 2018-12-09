import datetime
import sys, os
import math
import pickle
import threading
import tkinter as tk

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib.args import args_make_simulation_db
import simulator.sql
from lib import formula, make_logger
from lib import SCHEMA_PATH
from lib import Polling, elapsed_time
from lib.squares import put_on_square
from tools.make_simulation_db import init_nodes_table2
from lib.args import get_logger_args
global logger
logger_args = get_logger_args()
logger = make_logger(name=os.path.basename(__file__), level=logger_args.log_level)
logger.debug(f"__file__ = {__file__}")
logger.debug(f"__name__ = {__name__}")

try:
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except BaseException as e:
    logger.error('ERROR: PyOpenGL not installed properly.')
    logger.error(e)
    sys.exit()

def _normalize_milliseconds(seconds):
    return int(seconds * 1000)

def get_passed_milliseconds(passed_seconds):
    passed_milliseconds = _normalize_milliseconds(passed_seconds)
    return passed_milliseconds

class ManipulatingDB(Polling):
    SQUQRE_BODY = 0.011
    NODE_LEG = 0.033
    POLLING_SIMULATION_DB = 0.2

    def __init__(self, simulation_db_path, start_the_movie_time):
        Polling.__init__(self, self.POLLING_SIMULATION_DB)
        self.simulation_db_path = simulation_db_path
        self._initialized_db = False

        self.start_the_movie_time = start_the_movie_time
        self._old_passed_milliseconds = 0

        self.leave_there = threading.Event()
        self.stay_there = threading.Event()
        self.squares_lock = threading.Lock()
        self._squares = []
        self.label_area = LabelArea()

        self.node_squares = []

    def _init_maniplate_db(self):
        simulation_db = simulator.sql.SQL(db_path=self.simulation_db_path, schema_path=SCHEMA_PATH)
        self.simulation_db = simulation_db
        self.simulation_db.access_db()
        simulation_db.total_nodes = \
            self.simulation_db.select_one('simulation', 'total_nodes')
        column_name = 'simulation_milliseconds'
        self.simulation_milliseconds = \
            self.simulation_db.select('simulation', \
                             column_name)[0][column_name]
        self.the_running_milliseconds = self.simulation_milliseconds
        logger.info(f'{self}.the_running_milliseconds={self.the_running_milliseconds}')

        self._memory_db = simulator.sql.SQL(':memory:', schema_path=self.simulation_db.schema_path)
        self._memory_db.create_db()
        self._memory_db.create_table('simulation')
        init_nodes_table2(self._memory_db, simulation_db.total_nodes)

    def polling(self):
        if not self._initialized_db:
            self.initialized_db = True
            self._init_maniplate_db()
        passed_milliseconds = elapsed_time(self.start_the_movie_time)
        e = self.inhole_pickles_from_simlation_db(passed_milliseconds)

    def inhole_pickles_from_simlation_db(self, passed_milliseconds):
        # 0. simulation 開始時刻を 0 秒として，passed_milliseconds とは，
        #    simulation 経過秒数の事。
        #    現在とは，
        # 1. simulation 経過秒数を，passed_milliseconds に保存。

        # 2. s <= elapsed_time < passed_milliseconds を満たす record を
        #    memorydb 上の growings table から検索する。
        #    そして，現在の情報を，
        #    memorydb 上の nodes table に書き込む。
        conditions = \
            'where elapsed_time >= {} and elapsed_time < {}'. \
             format(self._old_passed_milliseconds, passed_milliseconds)
        logger.debug(f'conditions={conditions}')
        self._old_passed_milliseconds = passed_milliseconds
        records = self.simulation_db.select('growings', 'elapsed_time,pickle',
            conditions=conditions
        )
        logger.debug(f'records={records}, len(records)={len(records)}')

        if not records:
            return
        logger.info('conditions={}, len(records)={}'.format(conditions, len(records)))

        with self.squares_lock:
            self._squares.clear()
        for record in records:
            d = pickle.loads(record['pickle'])
            logger.info(f'{self} elapsed_time={record["elapsed_time"]}, d={d}')
            where = {'id': d['id']}
            self._memory_db.update('nodes', d, where)
            self._memory_db.commit()

        # 3. memorydb 上の nodes table の内容を，
        #    OpenGL の figures に変換する。
        nodes = self._memory_db.select('nodes')
        nodes = tuple(nodes)
        with self.squares_lock:
            self.node_squares.clear()
            for node in nodes:
                if node['status'] == 'active':
                    _keyID = int(node['key'][:10], 16)
                    r, x, y = formula._key2rxy(_keyID)
                    # node の居場所を記す，白い四角を書き込む。
                  # put_on_square(r, x, y, self.SQUQRE_BODY)
                    self.node_squares.append((r, x, y, self.SQUQRE_BODY))

        L = []
        for node in nodes:
            if node['status'] == 'active':
                L.append('id: {}, key: {}'.format(node['id'], node['key']))
        self.label_area.update('\n'.join(L))

    def completed_mission(self):
        self.leave_there.set()

    def is_continue(self):
        return not self.leave_there.is_set()

class MakingFigures(Polling):
    POLLING_SIMULATION_DB = 0.2

    def __init__(self, start_the_movie_time):
        Polling.__init__(self, self.POLLING_SIMULATION_DB)
        self.leave_there = threading.Event()
        self.stay_there = threading.Event()
        self.simulation_db = simulation_db
        self.start_the_movie_time = start_the_movie_time
        self.squares_lock = threading.Lock()
        self.lines_lock = threading.Lock()

    def polling(self):
        # 4. figures を OpenGL に書き込む。
        #    現在は，click した箇所付近の node を緑にしているだけ。
        with self.opengl_lock:
            with self.squares_lock:
                for square in self._squares:
                    put_on_square(*square)
            with self.lines_lock:
                for line in self._lines:
                    put_on_line(*line)

    def completed_mission(self):
        self.leave_there.set()

    def is_continue(self):
        return self.stay_there()

    def stay_there_(self):
        if self.leave_there.is_set():
            return False
        else:
            return True

class LabelArea(object):

    def run(self):
        self._tk_root = tk.Tk()
        self._buf = tk.StringVar()
        self._buf.set('')
        # justify=tk.LEFT で複数行の場合の文字列を左寄せ指定している。
        ft = font_tuple = ('Helvetica', '8')
        self.display = tk.Label(self._tk_root, textvariable=self._buf, font=ft,
                                bg='white', anchor=tk.W, justify=tk.LEFT)
        self.display.pack(side=tk.LEFT)
        self._tk_root.mainloop()

    def __init__(self):
        self._thread = threading.Thread(target=self.run)
        self._thread.start()

    def update(self, message):
        self._buf.set(message)

    def done(self):
        self.display.master.destroy()
        self.display.destroy()
        self.exit(0)

class Screen(object):
    def __init__(self, argv, simulation_db_path=None, width=500, height=500):
        logger.info(f"Screen(argv={argv}, width={width}, height={height})")
        self.frames = 0
        self.s = datetime.datetime.now()
        self.start_up_orig = self.s
        self.start_the_movie_time = self.s
        self._last_select_milliseconds = 0
        self.width = width
        self.height = height
        self.mode = GLUT_SINGLE | GLUT_RGBA
        # multi buffering
        self.mode |= GLUT_DOUBLE
        self.nodes = []
        self._squares = []
        self._debug = False
        self.opengl_lock = threading.Lock()
        self.lines_lock = threading.Lock()
        self.squares_lock = threading.Lock()

        self.simulation_db_path = simulation_db_path
        self.manipulating_db = ManipulatingDB(self.simulation_db_path, self.start_the_movie_time)
        self.manipulating_db.screen = self
       #self.making_figures = MakingFigures(self.start_the_movie_time)
#       self.making_frame = MakingFrame(self.start_the_movie_time)
#       self.construct_frame = ConstructFrame(self.start_the_movie_time)

        self.manipulating_db.start()
       #self.making_figures.start()
      # self.making_frame.start()
      # self.construct_frame.start()

        glutInit(argv)
        glutInitDisplayMode(self.mode)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(0, 0)
        glutCreateWindow(argv[0].encode())

        glutDisplayFunc(self._display)
        glutIdleFunc(glutPostRedisplay)
        glutKeyboardFunc(self._keyboard)
        glutMouseFunc(self.click_on)

    def set_display(self, display_main):
        glutMouseFunc(self.click_on_sample)
        self.display_main = display_main

    def set_db(self, db):
        self._db = db
        self._db.access_db()
      # init_nodes_table(self._db)

        column_name = 'simulation_milliseconds'
        self._memory_db = simulator.sql.SQL(':memory:', schema_path=self._db.schema_path)
        self._memory_db.create_db()
        self._memory_db.take_db(self._db)
        self._db.close()
        init_nodes_table(self._memory_db)

        self.simulation_milliseconds = \
            self._memory_db.select('simulation', \
                             column_name)[0][column_name]
        self.the_running_milliseconds = simulation_milliseconds
        logger.info(f'self.simulation_milliseconds={self.simulation_milliseconds}')

    def start(self):
        logger.info(f"{self}.start() start")
        glutMainLoop()
        logger.info(f"{self}.start() end")

    def update_nodes(self, nodes):
        self.nodes = nodes

    def _display(self):
        logger.info(f'{self}._display()')
        glClearColor(0, 0, 0, 0)
        # 以下の一行は重要
        glClear(GL_COLOR_BUFFER_BIT)

        passed_seconds = self._passed_time()

       #self.display_main(passed_seconds)
        self.display_main_thread(passed_seconds)

        glFlush()

        self.frames += 1

        # 地味だけど、重要
        glutSwapBuffers()

    def _print_fps(self):
        logger.info(f'{self}._print_fps()')
        ps = self._passed_time()
        fps = self.frames / ps
        logger.info(f'frames={self.frames}')
        logger.info(f'passed_seconds={ps:.3f}')
        logger.info(f'fps={fps:.3f}')

    def _simulation_info(self):
        logger.info(f'{self}._simulation_info()')
        self._print_fps()
      # print(dir(self.label_area.tk_root))
        label_area = self.manipulating_db.label_area
        logger.info(f'display={label_area.display}')
        logger.info(f'display.master={label_area.display.master}')
####### self.label_area.display.destroy()
####### if self.label_area.display.master:
#######     print('display.master.destroy()')
#######     help(self.label_area.display.master.destroy)
#######   # self.label_area.display.master.destroy()
#######     print('display.master.destroyed')
####### self.label_area._thread.destroy()
       #self.label_area.done()
       #raise()
####### self.label_area._tk_root.destroy()
      # self.label_area._thread.join(0.1)
      # self.label_area.join(0)
      # self.label_area.tk_root.master.destroy() master is None
      # self.label_area.tk_root.destroy() # 消せなくなる
      # self.label_area.tk_root.exit() # x
      # self.label_area.display.master.destroy() # 消せなくなる
      # self.label_area.master.destroy()
      # self.label_area.tk_root.destroy() # 消せなくなる

      # AttributeError: 'NoneType' object has no attribute 'destroy'
      # self.label_area.tk_root.master.destroy()
        count = 0
        for th in threading.enumerate():
            logger.info('count={}, th={}'.format(count, th))
            count += 1

#   def click_on(self, *event):
#       print('event={} in self.click_on()'.format(event))

    @staticmethod
    def get_current_cos_sin(x, y):
      # screen is monitor
      # print('GLUT_SCREEN_WIDTH =', glutGet(GLUT_SCREEN_WIDTH))
      # print('GLUT_SCREEN_HEIGHT =', glutGet(GLUT_SCREEN_HEIGHT))
      # glut window after changed
      # print('GLUT_WINDOW_WIDTH =', glutGet(GLUT_WINDOW_WIDTH))
      # print('GLUT_WINDOW_HEIGHT =', glutGet(GLUT_WINDOW_HEIGHT))
      # glut window when init
      # print('GLUT_INIT_WINDOW_WIDTH =', glutGet(GLUT_INIT_WINDOW_WIDTH))
      # print('GLUT_INIT_WINDOW_HEIGHT =', glutGet(GLUT_INIT_WINDOW_HEIGHT))
        ww = glutGet(GLUT_WINDOW_WIDTH)
        wh = glutGet(GLUT_WINDOW_HEIGHT)
        rate = ww / wh
        # math x, y axis
        # origin is window center
        # -ww / 2 <= x <= ww / 2
        # -wh / 2 <= y <= wh / 2
        mx = x - ww / 2
        my = wh / 2 - y
        logger.info(f'mx={mx} my={my}, x={x}, y={y} in self.click_on_sample()')

        # normalize
        norm_ww = ww / 2
        norm_wh = wh / 2 * rate
        norm_wd = math.sqrt(norm_ww ** 2 + norm_wh ** 2)
        norm_x = int(mx)
        norm_y = int(my * rate)
        norm_d = math.sqrt(norm_x ** 2 + norm_y ** 2)
        if norm_d == 0:
            logger.debug('norm_d={norm_d} in get_current_cos_sin()')
            return None, None, 0
        cos_ = norm_x / norm_d
        sin_ = norm_y / norm_d

        r = norm_ww
        # clickした箇所と原点(=単位円の中心)からの距離
        distance_ofclick_on_from_origin = norm_d / r
        docofo = distance_ofclick_on_from_origin

        logger.debug('distance_ofclick_on_from_origin={docofo} in get_current_cos_sin()')

        return cos_, sin_, docofo

    def click_on_sample(self, button, state, x, y):
        logger.info(f"{self}.click_on_sample(button={button}, state={state}, x={x}, y={y}")
        cos_, sin_, docofo = Screen.get_current_cos_sin(x, y)
        logger.info(f'cos_={cos_} sin_={sin_}, x={x}, y={y} in self.click_on_sample()')
        logger.info(f'distance_ofclick_on_from_origin={docofo} in click_on_sample()')

    def click_on(self, button, state, x, y):
        logger.info(f"{self}.click_on(button={button}, state={state}, x={x}, y={y}")
        if state != GLUT_DOWN:
            # mouse button を離した時などは速終了。
            # 参考
            # GLUT_LEFT_BUTTON
            # GLUT_MIDDLE_BUTTON
            # GLUT_RIGHT_BUTTON
            # GLUT_UP
            # GLUT_DOWN
            return
      # 左click 押した button=0, state=0, x=392, y=251  in self.click_on()
      # 左click 離した button=0, state=1, x=392, y=251  in self.click_on()
        logger.debug(f'button={button}, state={state}, x={x}, y={y} in self.click_on_sample()')

        cos_, sin_, docofo = Screen.get_current_cos_sin(x, y)

        band_width = 0.02
      # self._debug = True
        if math.fabs(1.0 - docofo) <= band_width:
            # 単位円の円周付近(=band_width) を click した。

            # click した箇所の，rad を計算。
            clicked_rad = formula.cos_sin_to_norm_rad(cos_, sin_)

            # click した箇所の前後 0.02 の範囲内にいる nodes を調べる。
            min_rad = clicked_rad - 0.02
            max_rad = clicked_rad + 0.02
            condition = '''
                where rad >= {} and rad <= {}
            '''.format(min_rad, max_rad)
            nodes = self._memory_db.select('nodes', conditions=condition)

            # click した箇所の前後 0.02 の範囲内にいる nodes を表示。
            logger.info(f'clicked nodes = {nodes}')
            for node in nodes:
                square = (node['rad'], node['x'], node['y'], 0.02, (0x00, 0xff, 0))
                self._squares.append(square)

    def _keyboard(self, key, x, y):
        logger.info(f"{self}._keyboard(key={key}, x={x}, y={y}")
        code = ord(key)
        logger.debug("")
        logger.debug('key={}, x={}, y={}, code={}'.format(key, x, y, code))
        if key.decode() == chr(27):
            logger.debug('ESC')
        if ord(key) == 27 or ord(key) == 0x17 or ord(key) == 0x03:
          # ESC              ctr-w               ctr-c
          # self.label_area._tk_root.destroy()
          # self.label_area.done()
            self._simulation_info()
          # self.label_area.display.destroy()
          # self.label_area.display.master.destroy()
            logger.debug('_keyboard() do sys.exit(0)')
            sys.exit(0)

    def display_main_thread(self, passed_seconds):
        logger.info(f'{self}.display_main_thread(passed_seconds={passed_seconds})')
        # 4. figures を OpenGL に書き込む。
        #    現在は，click した箇所付近の node を緑にしているだけ。
        with self.opengl_lock:
            with self.manipulating_db.squares_lock:
                for node_square in self.manipulating_db.node_squares:
                    put_on_square(*node_square)
              # for square in self._squares:
              #     put_on_square(*square)
          # with self.lines_lock:
          #     for line in self._lines:
          #         put_on_line(*line)
        if passed_seconds * 1000> self.manipulating_db.simulation_milliseconds:
            self._simulation_info()
            glutLeaveMainLoop()

    def display_main(self, passed_seconds):
        logger.info(f'{self}.display_main(passed_seconds={passed_seconds})')
        # 0. simulation 開始時刻を 0 秒として，passed_seconds とは，
        #    simulation 経過秒数の事。
        #    現在とは，simulation 経過秒数の事。
        # 1. 現在より1秒前(=s)と現在の時刻(=e)を，各々 s, e に格納。
        s, e = self.get_a_second_ago_and_now(passed_seconds)

        # 2. s <= elapsed_time < e を満たす record を
        #    memorydb 上の growings table から検索する。
        #    そして，現在の情報を，
        #    memorydb 上の nodes table に書き込む。
        conditions = \
            'where elapsed_time >= {} and elapsed_time < {}'. \
             format(self._last_select_milliseconds, e)
        logger.debug(f'conditions={conditions}')
        self._last_select_milliseconds = e
        records = self._memory_db.select('growings', 'elapsed_time,pickle',
            conditions=conditions
        )
        logger.debug(f'records={records}, len(records)={len(records)}')

        if len(records) >= 1:
            self._squares.clear()
            logger.info('conditions={}, len(records)={}'.format(conditions, len(records)))
            for record in records:
                d = pickle.loads(record['pickle'])
                logger.info('elapsed_time={}, d = {}'.format(record['elapsed_time'], d))
                where = {'id': d['id']}
                self._memory_db.update('nodes', d, where)
                self._memory_db.commit()

        # 3. memorydb 上の nodes table の内容を，
        #    OpenGL の figures に変換する。
        L = []
        nodes = self._memory_db.select('nodes')
        for node in nodes:
            if node['status'] == 'active':
                _keyID = int(node['key'][:10], 16)
                r, x, y = formula._key2rxy(_keyID)
                # node の居場所を記す，白い四角を書き込む。
                put_on_square(r, x, y, self.SQUQRE_BODY)
                L.append('id: {}, key: {}'.format(node['id'], node['key']))
        self.label_area.update('\n'.join(L))

        # 4. figures を OpenGL に書き込む。
        #    現在は，click した箇所付近の node を緑にしているだけ。
        for square in self._squares:
            put_on_square(*square)

    def get_a_second_ago_and_now(self, passed_seconds):
        milliseconds = _normalize_milliseconds(passed_seconds)
        e = milliseconds
        s = e - 1000
        if s < 0:
            s = 0
        if e > self.simulation_milliseconds:
            self._simulation_info()
            sys.exit(0)

        return s, e

    def _passed_time(self):
        e = datetime.datetime.now()
        return (e - self.s).total_seconds()

def display_sample(passed_seconds):
    moving = formula._fmove(passed_seconds)

    n = 100 # 100 個の点
    L = [] # 点の配置場所を tuple(rad, ix, iy) として格納

    # 点の配置場所を計算
    # ここでは rad は数学の定義と一致することに注意。
    # rad = 0,      x, y = cos(0), sin(0) = 1, 0
    # rad = pi / 2, x, y = cos(pi/2), sin(pi/2) = 0, 1
    for i in range(n):
        rate = i / n
        rad = 2 * math.pi * rate
        iy = math.sin(rad) * 0.99
        ix = math.cos(rad) * 0.99
        rxy = (rad, ix, iy)
        L.append(rxy)

    # 白い正方形を配置
    # white Quads
    half_pi = math.pi / 2.0
    for rxy in L:
        rad, ix, iy = rxy
        put_on_square(rad, ix, iy, 0.015)

    len_leg = 0.033
    glBegin(GL_LINES)
    for rxy in L:
        rx, ry, gx, gy = formula._moving_legs(rxy, moving, leg=len_leg)
        rad, ix, iy = rxy
        # 赤足
        glColor3ub(0xff, 0x00, 0x00)
        glVertex2f(ix, iy)
        glVertex2f(rx, ry)
        # 緑足
        glColor3ub(0x00, 0xff, 0x00)
        glVertex2f(ix, iy)
        glVertex2f(gx, gy)
    glEnd()
