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

WHITE=(0xff, 0xff, 0xff)
BLACK=(0x00, 0x00, 0x00)
RED=(0xff, 0, 0)
GREEN=(0, 0xff, 0)
BLUE=(0, 0, 0xff)
CYAN=(0x00, 0xff, 0xff)
MAGENTA=(0xff, 0x00, 0xff)
YELLOW=(0xff, 0xff, 0x00)
GLAY=(0x80, 0x80, 0x80)

HALF_PI = math.pi / 2.0
N_HALF_PIS = [None] * 4
for i in range(4):
    n_half_pi = i * HALF_PI
    N_HALF_PIS[i] = n_half_pi
N_HALF_PIS = tuple(N_HALF_PIS)

def put_on_square(r, x, y, leg, color=(0xff, 0xff, 0xff)):
    '''rは回転を制御する。x, yは軌道を制御する。'''
    glBegin(GL_QUADS)
    glColor3ub(*color)
    for i in range(4):
        wx = x + math.cos(r + N_HALF_PIS[i]) * leg
        wy = y + math.sin(r + N_HALF_PIS[i]) * leg
        glVertex2f(wx, wy)
    glEnd()

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
        self.moving_squares(passed_seconds)

    def moving_squares(self, passed_seconds):
        self._tick_tack(passed_seconds)
        self._rotating_square_on_origin(passed_seconds)
        self._rotating_square_around_origin(passed_seconds)
        self._moving_square_around_origin(passed_seconds)
        self._moving_square_around_origin_2(passed_seconds)
        self._rotating_square_around_origin_3(passed_seconds)
        self._rotating_square_around_origin_4(passed_seconds)
        self._rotating_square_around_origin_5(passed_seconds)
        self._rotating_square_around_origin_6(passed_seconds)
        self._rotating_square_around_origin_7(passed_seconds)
        self._rotating_square_around_origin_8(passed_seconds)
        self._rotating_square_around_origin_9(passed_seconds)
        self._rotating_square_around_origin_10(passed_seconds)
        self._rotating_square_around_origin_11(passed_seconds)
        self._rotating_square_around_origin_12(passed_seconds)
        self._rotating_square_around_origin_13(passed_seconds)
        self._rotating_square_around_origin_14(passed_seconds)
        self._rotating_square_around_origin_15(passed_seconds)
        self._rotating_square_around_origin_16(passed_seconds)

    def _moving_square_around_origin_2(self, passed_seconds):
        '''赤四角形が、原点を中心として時計回りで姿勢を変えずくるくる回る。'''
        ps = passed_seconds
        put_on_square(ps, math.cos(ps) / 4, math.sin(ps) / 4, 0.1, RED)

    def _moving_square_around_origin(self, passed_seconds):
        '''緑四角形が、原点を中心として時計回りで姿勢を変えずくるくる回る。'''
        ps = passed_seconds
        put_on_square(ps, math.cos(-ps) / 2, math.sin(-ps) / 2, 0.1, GREEN)

    def _rotating_square_around_origin(self, passed_seconds):
        '''青四角形が、原点を中心として時計回りで姿勢を変えずくるくる回る。'''
        ps = passed_seconds
        put_on_square(0, math.cos(-ps), math.sin(-ps), 0.1, BLUE)

    def _rotating_square_around_origin_3(self, passed_seconds):
        ps = passed_seconds
        put_on_square(-ps, math.cos(-ps) * 3 / 4, math.sin(-ps) * 3 / 4,
                       0.1, CYAN)

    def _rotating_square_around_origin_4(self, passed_seconds):
        ps = passed_seconds
        put_on_square(-ps, math.cos(ps) * 3 / 8, math.sin(ps) * 3 / 8,
                       0.1, MAGENTA)

    def _rotating_square_around_origin_5(self, passed_seconds):
        '''cos(), sin()の中身を適当にしてみたら横長の楕円軌道でした。'''
        ps = passed_seconds
        put_on_square(-ps, math.cos(-ps) * 5 / 8, math.sin(ps) * 3 / 8,
                       0.1, YELLOW)

    def _rotating_square_around_origin_6(self, passed_seconds):
        '''cos(), sin()の中身を適当にしてみたら_5の逆軌道でした。'''
        ps = passed_seconds
        put_on_square(-ps, math.cos(ps) * 5 / 8, math.sin(-ps) * 3 / 8,
                       0.1, GLAY)

    def _rotating_square_around_origin_7(self, passed_seconds):
        '''cos(), sin()の中身を適当に縦長の楕円軌道にする。'''
        ps = passed_seconds
        put_on_square(-ps, math.cos(ps) * 3 / 8, math.sin(-ps) * 8 / 8,
                       0.1, WHITE)

    '''_5, _6, _7でcos(), sin()の中身を調整して楕円軌道に出来たと思っていまし
       たが、そうではありませんでした。軌道の大きさを制御する変数に対して掛ける
       係数が等しくないため、楕円軌道となっていました。今気づきました。
    '''

    def _rotating_square_around_origin_8(self, passed_seconds):
        '''ということで、cos(), sin()の中身だけ変更して
           何が起こるのか探ってみます。'''
        ps = passed_seconds
        put_on_square(-ps, math.cos(-ps) * 3 / 8, math.sin(ps) * 8 / 8,
                       0.1, RED)
        '''楕円軌道が逆楕円軌道となりました。_5, _6で試していました。。。'''

    def _rotating_square_around_origin_9(self, passed_seconds):
        '''_8()に対してcos()の中身だけ正負を逆にして
           何が起こるのか探ってみます。'''
        ps = passed_seconds
        put_on_square(ps, math.cos(ps) * 3 / 8, math.sin(ps) * 8 / 8,
                      0.1, BLUE)
        '''軌道の変化は何も起こりませんでした。
           cos(x) = cos(-x) ですから当然ですね。
           というわけで、rotatingを負にして、逆回転させました。'''

    def _rotating_square_around_origin_10(self, passed_seconds):
        '''_8(), _9() の挙動から、_7()、つまり楕円軌道の白四角に対して
           sin()の中身の正負を逆にすると逆回転する気がするので試してみます。'''
        ps = passed_seconds
        put_on_square(-2 * ps, math.cos(ps) * 3 / 8, math.sin(ps) * 8 / 8,
                       0.1, GLAY)
        '''残念でしたー、逆"軌道"になるが正解でしたー。
           sin(x) = -sin(-x) ですから当然ですね。
           目で見るために倍速回転にしております。'''

    def _rotating_square_around_origin_11(self, passed_seconds):
        '''お遊びでお送りしております。'''
        ps = passed_seconds
        put_on_square(-2 * ps, math.cos(2*ps) * 3 / 8, math.sin(ps) * 8 / 8,
                       0.1, YELLOW)

    def _rotating_square_around_origin_12(self, passed_seconds):
        '''お遊びでお送りしております。'''
        ps = passed_seconds
        put_on_square(-2 * ps, math.cos(2*ps) * 3 / 8, math.sin(-2*ps) * 8 / 8,
                       0.1, RED)

    def _rotating_square_around_origin_13(self, passed_seconds):
        '''お遊びでお送りしております。'''
        '''こいつが一番好きだ。'''
        ps = passed_seconds
        put_on_square(-2 * ps, math.cos(ps) * 3 / 8, math.sin(2*ps) * 8 / 8,
                       0.05, BLUE)

    def _rotating_square_around_origin_14(self, passed_seconds):
        '''お遊びでお送りしております。'''
        ps = passed_seconds
        put_on_square(0, math.cos(ps), 0, 0.05, GREEN)

    def _rotating_square_around_origin_15(self, passed_seconds):
        '''お遊びでお送りしております。'''
        ps = passed_seconds
        put_on_square(0, 0, math.sin(ps), 0.05, GREEN)

    def _rotating_square_around_origin_16(self, passed_seconds):
        '''お遊びでお送りしております。'''
        '''こいつも好き。点滅させてみたりも。'''
        ps = passed_seconds
        if int(passed_seconds * 10) % 2 == 0:
            color = BLACK
        else:
            color = MAGENTA
        put_on_square(-2 * ps, math.cos(ps), math.sin(2*ps), 0.05, color)
      # equal to
      # if int(passed_seconds * 10) % 2 == 0:
      #     pass
      # else:
      #     put_on_square(-2 * ps, math.cos(ps), math.sin(2*ps), 0.05, MAGENTA)

    def _rotating_square_on_origin(self, passed_seconds):
        '''白四角形が、原点上を時計回りでくるくる回る。'''
        put_on_square(-passed_seconds, 0, 0, 0.1)

    def _tick_tack(self, passed_seconds):
        '''四角が 0 <= x <= pi / 2 の範囲で右往左往する。'''
        moving = formula._fmove(passed_seconds)

        glBegin(GL_QUADS)
        glColor3ub(0xff, 0xff, 0xff)
        half_pi = math.pi / 2.0

        leg = 0.02
        # 0 <= moving <= pi / 4
        rad = moving * 2
        x = math.cos(rad) * 0.98
        y = math.sin(rad) * 0.98
        for i in range(4):
            n_half_pi = i * half_pi
            wx = x + math.cos(n_half_pi) * leg
            wy = y + math.sin(n_half_pi) * leg
            glVertex2f(wx, wy)
        glEnd()

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
