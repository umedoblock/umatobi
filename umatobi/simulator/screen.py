import datetime
import sys
import math

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
        moving = formula._fmove(passed_seconds)

        self.display_main(moving)

        glFlush()
        d = datetime.datetime.today()
        print('\r{}, {:.6f}'.format(d, moving), end='')

        self.frames += 1

        # 地味だけど、重要
        glutSwapBuffers()

    def _keyboard(self, key, x, y):
        code = ord(key)
        print()
        print('key={}, x={}, y={}, code={}'.format(key, x, y, code))
        if key.decode() == chr(27):
            print('ESC')
        if ord(key) == 27:
            # 'ESC'

            passed_seconds = self._passed_time()
            print('passed_seconds =', passed_seconds)
            fps = self.frames / passed_seconds
            print('fps =', fps)

            sys.exit(0)

    def _passed_time(self):
        e = datetime.datetime.today()
        return (e - self.s).total_seconds()

def display_sample(moving):
    n = 100 # 100 個の点
    L = [] # 点の配置場所を tuple(rad, ix, iy) として格納

    # 点を円形に配置
    # 点の配置場所を計算
    for i in range(n):
        rate = i / n
        rad = 2 * math.pi * rate
        iy = math.sin(rad) * 0.99
        ix = math.cos(rad) * 0.99
        rxy = (rad, ix, iy)
        L.append(rxy)
    # 大きさ3の白い点を描画
    glPointSize(3)
    glBegin(GL_POINTS)
    glColor3ub(0xff, 0xff, 0xff)
    for rxy in L:
        rad, ix, iy = rxy
        glVertex2f(ix, iy)
    glEnd()

    len_leg = 0.033
    glBegin(GL_LINES)

    # white line
    for rxy in L:
        rad, ix, iy = rxy
        wx = math.cos(rad + math.pi) * len_leg * 2 + ix
        wy = math.sin(rad + math.pi) * len_leg * 2 + iy
        glColor3ub(0xff, 0xff, 0xff)
        glVertex2f(ix, iy)
        glVertex2f(wx, wy)

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
