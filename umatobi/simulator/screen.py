import datetime, time
import sys, os
import math
import pickle
import threading
import tkinter as tk

from umatobi.log import *
from umatobi.constants import *
from umatobi.lib.args import args_make_simulation_db
from umatobi.simulator import sql
from umatobi.lib import formula
from umatobi.lib import Polling, elapsed_time
from umatobi.lib.squares import put_on_square
from umatobi.lib.formula import get_current_cos_sin_in_window
from umatobi.lib import get_passed_seconds, get_passed_ms
from umatobi.tools.make_simulation_db import init_nodes_table2

try:
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except BaseException as e:
    logger.error('ERROR: PyOpenGL not installed properly.')
    logger.error(e)
    sys.exit()

def get_current_cos_sin(x, y):
    ww = glutGet(GLUT_WINDOW_WIDTH)
    wh = glutGet(GLUT_WINDOW_HEIGHT)

    logger.debug(f"get_current_cos_sin_in_window(ww={ww} wh={wh}, x={x}, y={y})")

    cos_, sin_, docofo = get_current_cos_sin_in_window(ww, wh, x, y)
    if (cos_, sin_) == (None, None):
        logger.debug(f"get_current_cos_sin_in_window(), clicked origin.")
    logger.info(f"get_current_cos_sin_in_window(), cos_={cos_}, sin_={sin_}, docofo={docofo}")
    return cos_, sin_, docofo

class Screen(object):
    def __init__(self, argv, simulation_db_path=None, display=None, width=500, height=500):
        logger.info(f"""Screen(self={self},
                        argv={argv},
                        simulation_db_path={simulation_db_path},
                        display={display},
                        width={width},
                        height={height})""")
        self.frames = 0
        self.start_the_movie_time = datetime.datetime.now()
        self.width = width
        self.height = height
        self.mode = GLUT_SINGLE | GLUT_RGBA | GLUT_DOUBLE
        self._debug = False

        self.simulation_db_path = simulation_db_path
        if simulation_db_path:
            self.manipulating_db = ManipulatingDB(self.simulation_db_path, self.start_the_movie_time)
            self.manipulating_db.screen = self
            self.manipulating_db.start()
            self.manipulating_db.manipulated.wait()

        if display is None:
            self.display_main = self.display_main_thread
        else:
            self.display_main = display
        self._glut_init(argv, self.mode, width, height)

    def _glut_init(self, argv, mode, w, h):
        logger.info(f"""{self}._glut_init(argv={argv},
                        mode={mode},
                        w={w},
                        h={h}""")

        glutInit(argv)
        glutInitDisplayMode(mode)
        glutInitWindowSize(w, h)
        glutInitWindowPosition(0, 0)
        glutCreateWindow(argv[0].encode())

        glutDisplayFunc(self._display)
        glutIdleFunc(glutPostRedisplay)
        glutKeyboardFunc(self._keyboard)
        glutMouseFunc(self.click_on)

    def set_display(self, display):
        logger.debug(f"{self}.set_display({display})")
        self.display_main = display

    def start(self):
        logger.info(f"{self}.start() start")
        glutMainLoop()
        logger.info(f"{self}.start() end")

    def _display(self):
      # logger.info(f"{self}._display()") # 多すぎて邪魔
        glClearColor(0, 0, 0, 0)
        # 以下の一行は重要
        glClear(GL_COLOR_BUFFER_BIT)

        passed_seconds = get_passed_seconds(self.start_the_movie_time)
        logger.debug(f"{self}._display(), get_passed_seconds({self.start_the_movie_time}={passed_seconds})")
        self.display_main(self, passed_seconds)

        self.frames += 1

        # 地味だけど、重要
        glutSwapBuffers()

    def display_main_thread(self, passed_seconds):
        logger.debug(f"{self}.display_main_thread(passed_seconds={passed_seconds})")
        # 4. figures を OpenGL に書き込む。
        #    現在は，click した箇所付近の node を緑にしているだけ。
        moving = formula._fmove(passed_seconds)
        with self.manipulating_db.squares_lock:
            logger.debug(f"{self}.manipulating_db.squares_lock.acquire()")
            logger.debug(f"{self}.manipulating_db.node_squares={self.manipulating_db.node_squares}")
            for node_square in self.manipulating_db.node_squares:
                put_on_square(*node_square)
                logger.debug(f"put_on_square(*node_square={node_square}")

            logger.debug(f"{self}.manipulating_db.green_squares={self.manipulating_db.green_squares}")
            for green_square in self.manipulating_db.green_squares:
                put_on_square(*green_square)
                logger.debug(f"put_on_square(*green_square={green_square}")

            glBegin(GL_LINES)
            for rxy in self.manipulating_db.node_legs:
                rx, ry, gx, gy = formula._moving_legs(rxy, moving)
                rad, ix, iy = rxy
                legs = ix, iy, rx, ry, gx, gy
                # 赤足
                glColor3ub(0xff, 0x00, 0x00)
                glVertex2f(ix, iy)
                glVertex2f(rx, ry)
                # 緑足
                glColor3ub(0x00, 0xff, 0x00)
                glVertex2f(ix, iy)
                glVertex2f(gx, gy)
            glEnd()
            logger.debug(f"{self}.manipulating_db.squares_lock.release()")

        if get_passed_ms(self.start_the_movie_time) > self.manipulating_db.simulation_ms:
            logger.info(f"get_passed_ms({self.start_the_movie_time}) > {self.manipulating_db.simulation_ms}")
            self._simulation_info()
            glutLeaveMainLoop()

    def _print_fps(self):
        passed_seconds = get_passed_seconds(self.start_the_movie_time)
        fps = self.frames / passed_seconds
        logger.info(f"""{self}._print_fps()
                      frames={self.frames}
                      passed_seconds={passed_seconds:.3f}
                      fps={fps:.3f}""")

    def _simulation_info(self):
        self._print_fps()
        label_area = self.manipulating_db.label_area
        logger.info(f"""{self}._simulation_info()
                        label_area={label_area}
                        display={label_area.display}
                        display.master={label_area.display.master}""")
        for count, th in enumerate(threading.enumerate()):
            logger.debug(f"{self}._simulation_info(), thread={th}, count={count}")

    def _keyboard(self, key, x, y):
        code = ord(key)
        logger.info(f"{self}._keyboard(key={key}, x={x}, y={y}), code={code}")
        if key.decode() == chr(27):
            logger.debug('ESC')
        if ord(key) == 27 or ord(key) == 0x17 or ord(key) == 0x03:
          # ESC              ctr-w               ctr-c
            self._simulation_info()
            logger.info(f"{self}._keyboard(), sys.exit(0)")
            sys.exit(0)

    def click_on_sample(self, button, state, x, y):
        logger.info(f"{self}.click_on_sample(button={button}, state={state}, x={x}, y={y}")
        cos_, sin_, docofo = get_current_cos_sin(x, y)
        logger.debug(f"{self}.click_on_sample(), cos_={cos_} sin_={sin_}, docofo={docofo}, x={x}, y={y}")

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

        cos_, sin_, docofo = get_current_cos_sin(x, y)

        band_width = 0.02
      # self._debug = True
        if math.fabs(1.0 - docofo) <= band_width:
            # 単位円の円周付近(=band_width) を click した。

            # click した箇所の，rad を計算。
            clicked_rad = formula.cos_sin_to_norm_rad(cos_, sin_)
            logger.debug(f"clicked_rad={clicked_rad}, formula.cos_sin_to_norm_rad(cos_={cos_}, sin_={sin_}")

            min_rad = clicked_rad - 0.02
            max_rad = clicked_rad + 0.02

            clicked_rad_range = (min_rad, max_rad)
            crr = clicked_rad_range
            # click した箇所の前後 0.02 の範囲を記憶。
            with self.manipulating_db.squares_lock:
                self.manipulating_db.clicked_rad_ranges.append(crr)

    def idle(self):
        # 4. figures を OpenGL に書き込む。
        #    現在は，click した箇所付近の node を緑にしているだけ。
        with self.manipulating_db.squares_lock:
            for node_square in self.manipulating_db.node_squares:
                put_on_square(*node_square)

        glutPostRedisplay()

class ManipulatingDB(threading.Thread):
    SQUQRE_BODY = 0.011
    NODE_LEG = 0.033
    POLLING_SIMULATION_DB = 0.2

    def __init__(self, simulation_db_path, start_the_movie_time):
        threading.Thread.__init__(self)

        logger.info(f"""ManipulatingDB(self={self},
                      simulation_db_path={simulation_db_path},
                      start_the_movie_time={start_the_movie_time}""")
        self.polling_secs = self.POLLING_SIMULATION_DB
        logger.debug(f"{self}.polling_secs={self.polling_secs}")
        self.simulation_db_path = simulation_db_path
        self._initialized_db = False

        self.start_the_movie_time = start_the_movie_time
        self._old_passed_ms = 0

        self.leave_there = threading.Event()
        self.stay_there = threading.Event()
        self.manipulated = threading.Event()
        self.squares_lock = threading.Lock()
        self.label_area = LabelArea()

        self.node_squares = []
        self.green_squares = []
        self.node_legs = []
        self.clicked_rad_ranges = []

    def _init_maniplate_db(self):
        logger.debug(f"{self}._init_maniplate_db()")
        simulation_db = sql.SQL(db_path=self.simulation_db_path, schema_path=SCHEMA_PATH)
        self.simulation_db = simulation_db
        self.simulation_db.access_db()
        simulation_db.total_nodes = \
            self.simulation_db.select_one('simulation', 'total_nodes')
        column_name = 'simulation_ms'
        self.simulation_ms = \
            self.simulation_db.select('simulation', \
                             column_name)[0][column_name]

        logger.debug(f"{self}._init_maniplate_db(), {self}.simulation_ms={self.simulation_ms}")
        self._memory_db = sql.SQL(':memory:', schema_path=self.simulation_db.schema_path)
        logger.debug(f"{self}._init_maniplate_db(), {self}._memory_db={self._memory_db}")
        self._memory_db.create_db()
        self._memory_db.create_table('simulation')
        init_nodes_table2(self._memory_db, simulation_db.total_nodes)
        self.manipulated.set()

    def run(self):
        logger.info(f"{self}.run()")
        self._init_maniplate_db()
        while True:
            passed_ms = get_passed_ms(self.start_the_movie_time)
            e = self.inhole_pickles_from_simlation_db(passed_ms)
            time.sleep(self.polling_secs)

    def inhole_pickles_from_simlation_db(self, passed_ms):
        # 0. simulation 開始時刻を 0 秒として，passed_ms とは，
        #    simulation 経過秒数の事。
        #    現在とは，
        # 1. simulation 経過秒数を，passed_ms に保存。

        # 2. s <= elapsed_time < passed_ms を満たす record を
        #    memorydb 上の growings table から検索する。
        #    そして，現在の情報を，
        #    memorydb 上の nodes table に書き込む。
      # logger.info(f"{self}.inhole_pickles_from_simlation_db(passed_ms={passed_ms})") # 多すぎて邪魔
        conditions = f"where elapsed_time >= {self._old_passed_ms} and elapsed_time < {passed_ms}"
        logger.debug(f"{self}.inhole_pickles_from_simlation_db(), conditions={conditions}")
        self._old_passed_ms = passed_ms
        records = self.simulation_db.select('growings', 'elapsed_time,pickle',
            conditions=conditions
        )
        logger.debug(f"{self}.inhole_pickles_from_simlation_db(), len(records)={len(records)}, records={records}")

        for record in records:
            d = pickle.loads(record['pickle'])
            logger.debug(f"{self}.inhole_pickles_from_simlation_db(), elapsed_time={record['elapsed_time']}, pickle.loads(record['pickle'])={d}")
            where = {'id': d['id']}
            self._memory_db.update('nodes', d, where)
            self._memory_db.commit()

        node_squares = []
        green_squares = []
        node_legs = []

        with self.squares_lock:
            clicked_rad_ranges = self.clicked_rad_ranges.copy()

        # 3. memorydb 上の nodes table の内容を，
        #    OpenGL の figures に変換する。
        nodes = tuple(self._memory_db.select('nodes'))
        logger.debug(f"{self}.inhole_pickles_from_simlation_db(), self._memory_db.select('nodes')={nodes}")
        for node in nodes:
            logger.debug(f"{self}.inhole_pickles_from_simlation_db(), node={node}, node.keys()={node.keys()}, tuple(node)={tuple(node)}")
            if node['status'] == 'active':
                _keyID = int(node['key'][:10], 16)
                r, x, y = formula._key2rxy(_keyID)
                r_ = r
                r = -r + math.pi / 2
                rxy = (r, x, y)
                node_legs.append(rxy)
                logger.debug(f"""{self}.inhole_pickles_from_simlation_db(),
                                node_legs.append({rxy})""")
                # node の居場所を記す，白い四角を書き込む。
                node_squares.append((r, x, y, self.SQUQRE_BODY))
                logger.debug(f"node_squares.append({(r, x, y, self.SQUQRE_BODY)})")
                for clicked_rad_range in clicked_rad_ranges:
                    min_rad, max_rad = clicked_rad_range
                    if min_rad <= r_ <= max_rad:
                        # click 箇所付近のnodeであれば，緑の四角を置く。
                        logger.debug(f"{self}.inhole_pickles_from_simlation_db(), found a node(r={r_}) in range({min_rad}, {max_rad})")
                        green_square = (r_, x, y, 0.02, (0x00, 0xff, 0))
                        green_squares.append(green_square)
                        break
        with self.squares_lock:
            logger.debug(f"""{self}.inhole_pickles_from_simlation_db(),
                             {self.squares_lock}.acquire()""")
            self.node_squares = node_squares
            self.green_squares = green_squares
            self.node_legs = node_legs
            logger.debug(f"""{self}.inhole_pickles_from_simlation_db(),
                             {self.squares_lock}.release()""")

        L = []
        for node in nodes:
            if node['status'] == 'active':
                L.append(f"id: {node['id']}, key: {node['key']}")
        self.label_area.update('\n'.join(L))
        logger.debug(f"""{self}.inhole_pickles_from_simlation_db(),
                         {self.label_area}.update({'/n'.join(L)})""")

    def completed_mission(self):
        self.leave_there.set()

    def is_continue(self):
        return not self.leave_there.is_set()

class LabelArea(object):

    def __init__(self):
        self._thread = threading.Thread(target=self.run)
        logger.info(f"LabelArea(self={self})")
        self._thread.start()

    def run(self):
        logger.info(f"{self}.run()")
        self._tk_root = tk.Tk()
        self._buf = tk.StringVar()
        self._buf.set('')
        # justify=tk.LEFT で複数行の場合の文字列を左寄せ指定している。
        ft = font_tuple = ('Helvetica', '8')
        self.display = tk.Label(self._tk_root, textvariable=self._buf, font=ft,
                                bg='white', anchor=tk.W, justify=tk.LEFT)
        self.display.pack(side=tk.LEFT)
        self._tk_root.mainloop()

    def update(self, message):
        logger.debug(f"{self}.update()")
        self._buf.set(message)

    def done(self):
        logger.info(f"{self}.done()")
        self.display.master.destroy()
        self.display.destroy()
        self.exit(0)

class Trailer(object):
    def __init__(self, argv, display=None, width=500, height=500):
        logger.info(f"""Trailer(self={self},
        argv={argv},
        display={display},
        width={width},
        height={height})""")
        self.frames = 0
        self.open_the_theater = datetime.datetime.now()
        self.width = width
        self.height = height
        self.mode = GLUT_SINGLE | GLUT_RGBA | GLUT_DOUBLE
        self._debug = False
        self.start_the_movie_time = datetime.datetime.now()

        self.display_main = display
        self._glut_init(argv, self.mode, width, height)

    def _glut_init(self, argv, mode, w, h):
        logger.info(f"""{self}._glut_init(argv={argv},
        mode={mode},
        w={w},
        h={h}""")

        glutInit(argv)
        glutInitDisplayMode(mode)
        glutInitWindowSize(w, h)
        glutInitWindowPosition(0, 0)
        glutCreateWindow(argv[0].encode())

        glutDisplayFunc(self._display)
        glutIdleFunc(glutPostRedisplay)
        glutKeyboardFunc(self.keyboard)
        glutMouseFunc(self.click_on_sample)

    def start(self):
        logger.info(f"{self}.start() start")
        glutMainLoop()
        logger.info(f"{self}.start() end")

    def _display(self):
      # logger.info(f"{self}._display()") # 多すぎて邪魔。
        glClearColor(0, 0, 0, 0)
        # 以下の一行は重要
        glClear(GL_COLOR_BUFFER_BIT)

        passed_seconds = get_passed_seconds(self.open_the_theater)
      # logger.debug(f"""{self}._display(),
      #                  get_passed_seconds({self.open_the_theater})=
      #                  {passed_seconds}""")
        self.display_main(passed_seconds)

        self.frames += 1

        # 地味だけど、重要
        glutSwapBuffers()

    def print_fps(self):
        passed_seconds = get_passed_seconds(self.start_the_movie_time)
        fps = self.frames / passed_seconds
        logger.info(f"""{self}.print_fps()
                      frames={self.frames}
                      passed_seconds={passed_seconds:.3f}
                      fps={fps:.3f}""")

    def simulation_info(self):
        logger.info(f"{self}.simulation_info()")
        self.print_fps()
        count = 0
        for th in threading.enumerate():
            logger.debug(f"thread={th}, count={count}")
            count += 1

    def click_on_sample(self, button, state, x, y):
        logger.info(f"""{self}.click_on_sample(button={button},
                        state={state},
                        x={x},
                        y={y}""")
        cos_, sin_, docofo = get_current_cos_sin(x, y)
        logger.debug(f"""{self}.click_on_sample(),
                         cos_={cos_}
                         sin_={sin_},
                         docofo={docofo},
                         x={x},
                         y={y}""")

    def keyboard(self, key, x, y):
        code = ord(key)
        logger.info(f"{self}.keyboard(key={key}, x={x}, y={y}), code={code}")
        if key.decode() == chr(27):
            logger.debug('ESC')
        if ord(key) == 27 or ord(key) == 0x17 or ord(key) == 0x03:
          # ESC              ctr-w               ctr-c
            self.simulation_info()
            logger.info(f"{self}.keyboard(), sys.exit(0)")
            sys.exit(0)

def display_sample(passed_seconds):
    n = 100 # 100 個の点

    moving = formula._fmove(passed_seconds)
    logger.info(f"""display_sample(passed_seconds={passed_seconds}),
                    moving={moving}""")
    length_circle = 2 * math.pi * 1.0
    length_legs = length_circle / (2 * n)

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

    glBegin(GL_LINES)
    for rxy in L:
        rx, ry, gx, gy = formula._moving_legs(rxy, moving, leg=length_legs)
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
