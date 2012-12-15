import datetime
import sys
import math
import pickle

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib.args import args_make_simulation_db
import simulator.sql
from lib import formula
from lib.squares import put_on_square

try:
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except BaseException as e:
    print('''ERROR: PyOpenGL not installed properly.''')
    print(e)
    sys.exit()

def _normalize_milliseconds(seconds):
    return int(seconds * 1000)

class Screen(object):
    def __init__(self, argv, pixel=500):
        self.frames = 0
        self.s = datetime.datetime.now()
        self.pixel = pixel
        width = height = pixel
        self.mode = GLUT_SINGLE | GLUT_RGBA
        # multi buffering
        self.mode |= GLUT_DOUBLE
        self.nodes = []

        glutInit(argv)
        glutInitDisplayMode(self.mode)
        glutInitWindowSize(width, height)
        glutInitWindowPosition(0, 0)
        glutCreateWindow(argv[0].encode())

        glutDisplayFunc(self._display)
        glutIdleFunc(glutPostRedisplay)
        glutKeyboardFunc(self._keyboard)

    def set_display(self, display_main):
        self.display_main = display_main

    def set_db(self, db):
        self._db = db
        self._db.access_db()
        column_name = 'simulation_milliseconds'
        self.simulation_milliseconds = \
            self._db.select('simulation', \
                             column_name)[0][column_name]
        print('self.simulation_milliseconds =', self.simulation_milliseconds)

    def start(self):
        glutMainLoop()

    def update_nodes(self, nodes):
        self.nodes = nodes

    def _display(self):
        glClearColor(0, 0, 0, 0)
        # 以下の一行は重要
        glClear(GL_COLOR_BUFFER_BIT)

        passed_seconds = self._passed_time()

        self.display_main(passed_seconds)

        glFlush()

        self.frames += 1

        # 地味だけど、重要
        glutSwapBuffers()

    def _keyboard(self, key, x, y):
        code = ord(key)
        print()
        print('key={}, x={}, y={}, code={}'.format(key, x, y, code))
        if key.decode() == chr(27):
            print('ESC')
        if ord(key) == 27 or ord(key) == 0x17 or ord(key) == 0x03:
          # ESC              ctr-w               ctr-c

            passed_seconds = self._passed_time()
            print('passed_seconds =', passed_seconds)
            fps = self.frames / passed_seconds
            print('fps =', fps)

            sys.exit(0)

    def display_main(self, passed_seconds):
        milliseconds = _normalize_milliseconds(passed_seconds)
        s = milliseconds - 1000
        if s < 0:
            s = 0
        if s > self.simulation_milliseconds:
            sys.exit(0)
        e = milliseconds
        print('\re = {:7d}'.format(e), end='')

        conditions = \
            'where elapsed_time >= {} and elapsed_time < {}'.format(s, e)
        records = self._db.select('growings', 'elapsed_time,pickle',
            conditions=conditions
        )

      # print('conditions =', conditions)
      # print('milliseconds = {}, len(records) = {}'. \
      #        format(milliseconds, len(records)))
        if len(records) >= 1:
            len_body = 0.011
            len_leg = 0.033
            for record in records:
                d = pickle.loads(record['pickle'])
              # print('d =', d)
                if d['key'] is not None:
                    _keyID = int(d['key'][:10], 16)
                    r, x, y = formula._key2rxy(_keyID)

                    put_on_square(r, x, y, len_body)

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
