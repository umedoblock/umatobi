import datetime
import sys
import math

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib.args import args_make_simulation_db
import simulator.sql

from lib import formula

try:
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except BaseException as e:
    print('''ERROR: PyOpenGL not installed properly.''')
    print(e)
    sys.exit()

class Screen(object):
    def __init__(self, argv, pixel=500):
        self.frames = 0
        self.s = datetime.datetime.today()
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
        d = datetime.datetime.today()
      # print('\r{}, {:.6f}'.format(d, moving), end='')
        print('\r{}'.format(d), end='')

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
        pass

    def _passed_time(self):
        e = datetime.datetime.today()
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

    len_leg = 0.033

    # 白い正方形を配置
    # white Quads
    glBegin(GL_QUADS)
    glColor3ub(0xff, 0xff, 0xff)
    half_pi = math.pi / 2.0
    for rxy in L:
        rad, ix, iy = rxy
        for i in range(4):
            n_half_pi = i * half_pi
            wx = math.cos(rad + n_half_pi) * len_leg / 3 + ix
            wy = math.sin(rad + n_half_pi) * len_leg / 3 + iy
            glVertex2f(wx, wy)
    glEnd()

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
