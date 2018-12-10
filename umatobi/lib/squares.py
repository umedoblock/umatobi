import math, sys

try:
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except BaseException as e:
    print('''ERROR: PyOpenGL not installed properly.''')
    print(e)
    sys.exit()

from . import formula

HALF_PI = math.pi / 2.0
N_HALF_PIS = [None] * 4
for i in range(4):
    n_half_pi = i * HALF_PI
    N_HALF_PIS[i] = n_half_pi
N_HALF_PIS = tuple(N_HALF_PIS)

WHITE=(0xff, 0xff, 0xff)
BLACK=(0x00, 0x00, 0x00)
RED=(0xff, 0, 0)
GREEN=(0, 0xff, 0)
BLUE=(0, 0, 0xff)
CYAN=(0x00, 0xff, 0xff)
MAGENTA=(0xff, 0x00, 0xff)
YELLOW=(0xff, 0xff, 0x00)
GLAY=(0x80, 0x80, 0x80)

def put_on_square(r, x, y, leg, color=(0xff, 0xff, 0xff)):
    '''rは回転を制御する。x, yは軌道を制御する。'''
    glBegin(GL_QUADS)
    put_on_squares(r, x, y, leg, color)
    glEnd()

def put_on_squares(r, x, y, leg, color=(0xff, 0xff, 0xff)):
    '''rは回転を制御する。x, yは軌道を制御する。'''
    glColor3ub(*color)
    for i in range(4):
        wx = x + math.cos(r + N_HALF_PIS[i]) * leg
        wy = y + math.sin(r + N_HALF_PIS[i]) * leg
        glVertex2f(wx, wy)

def _moving_squares(passed_seconds):
    _tick_tack(passed_seconds)
    _rotating_square_on_origin(passed_seconds)
    _rotating_square_around_origin(passed_seconds)
    _moving_square_around_origin(passed_seconds)
    _moving_square_around_origin_2(passed_seconds)
    _rotating_square_around_origin_3(passed_seconds)
    _rotating_square_around_origin_4(passed_seconds)
    _rotating_square_around_origin_5(passed_seconds)
    _rotating_square_around_origin_6(passed_seconds)
    _rotating_square_around_origin_7(passed_seconds)
    _rotating_square_around_origin_8(passed_seconds)
    _rotating_square_around_origin_9(passed_seconds)
    _rotating_square_around_origin_10(passed_seconds)
    _rotating_square_around_origin_11(passed_seconds)
    _rotating_square_around_origin_12(passed_seconds)
    _rotating_square_around_origin_13(passed_seconds)
    _rotating_square_around_origin_14(passed_seconds)
    _rotating_square_around_origin_15(passed_seconds)
    _rotating_square_around_origin_16(passed_seconds)

def _tick_tack(passed_seconds):
    '''四角が 0 <= x <= pi / 2 の範囲で右往左往する。'''
    moving = formula._fmove(passed_seconds)

    glColor3ub(0xff, 0xff, 0xff)

    leg = 0.02
    # 0 <= moving <= pi / 4
    turn = math.pi / 2
    q, r = divmod(passed_seconds, turn)
    if int(q % 2) == 0:
        rad = r
    else:
        rad = turn - r
    x = math.cos(rad) * 0.98
    y = math.sin(rad) * 0.98
    put_on_square(rad, x, y, leg)

def _moving_square_around_origin_2(passed_seconds):
    '''赤四角形が、原点を中心として時計回りで姿勢を変えずくるくる回る。'''
    ps = passed_seconds
    put_on_square(ps, math.cos(ps) / 4, math.sin(ps) / 4, 0.1, RED)

def _moving_square_around_origin(passed_seconds):
    '''緑四角形が、原点を中心として時計回りで姿勢を変えずくるくる回る。'''
    ps = passed_seconds
    put_on_square(ps, math.cos(-ps) / 2, math.sin(-ps) / 2, 0.1, GREEN)

def _rotating_square_around_origin(passed_seconds):
    '''青四角形が、原点を中心として時計回りで姿勢を変えずくるくる回る。'''
    ps = passed_seconds
    put_on_square(0, math.cos(-ps), math.sin(-ps), 0.1, BLUE)

def _rotating_square_around_origin_3(passed_seconds):
    ps = passed_seconds
    put_on_square(-ps, math.cos(-ps) * 3 / 4, math.sin(-ps) * 3 / 4,
                   0.1, CYAN)

def _rotating_square_around_origin_4(passed_seconds):
    ps = passed_seconds
    put_on_square(-ps, math.cos(ps) * 3 / 8, math.sin(ps) * 3 / 8,
                   0.1, MAGENTA)

def _rotating_square_around_origin_5(passed_seconds):
    '''cos(), sin()の中身を適当にしてみたら横長の楕円軌道でした。'''
    ps = passed_seconds
    put_on_square(-ps, math.cos(-ps) * 5 / 8, math.sin(ps) * 3 / 8,
                   0.1, YELLOW)

def _rotating_square_around_origin_6(passed_seconds):
    '''cos(), sin()の中身を適当にしてみたら_5の逆軌道でした。'''
    ps = passed_seconds
    put_on_square(-ps, math.cos(ps) * 5 / 8, math.sin(-ps) * 3 / 8,
                   0.1, GLAY)

def _rotating_square_around_origin_7(passed_seconds):
    '''cos(), sin()の中身を適当に縦長の楕円軌道にする。'''
    ps = passed_seconds
    put_on_square(-ps, math.cos(ps) * 3 / 8, math.sin(-ps) * 8 / 8,
                   0.1, WHITE)

'''_5, _6, _7でcos(), sin()の中身を調整して楕円軌道に出来たと思っていまし
   たが、そうではありませんでした。軌道の大きさを制御する変数に対して掛ける
   係数が等しくないため、楕円軌道となっていました。今気づきました。
'''

def _rotating_square_around_origin_8(passed_seconds):
    '''ということで、cos(), sin()の中身だけ変更して
       何が起こるのか探ってみます。'''
    ps = passed_seconds
    put_on_square(-ps, math.cos(-ps) * 3 / 8, math.sin(ps) * 8 / 8,
                   0.1, RED)
    '''楕円軌道が逆楕円軌道となりました。_5, _6で試していました。。。'''

def _rotating_square_around_origin_9(passed_seconds):
    '''_8()に対してcos()の中身だけ正負を逆にして
       何が起こるのか探ってみます。'''
    ps = passed_seconds
    put_on_square(ps, math.cos(ps) * 3 / 8, math.sin(ps) * 8 / 8,
                  0.1, BLUE)
    '''軌道の変化は何も起こりませんでした。
       cos(x) = cos(-x) ですから当然ですね。
       というわけで、rotatingを負にして、逆回転させました。'''

def _rotating_square_around_origin_10(passed_seconds):
    '''_8(), _9() の挙動から、_7()、つまり楕円軌道の白四角に対して
       sin()の中身の正負を逆にすると逆回転する気がするので試してみます。'''
    ps = passed_seconds
    put_on_square(-2 * ps, math.cos(ps) * 3 / 8, math.sin(ps) * 8 / 8,
                   0.1, GLAY)
    '''残念でしたー、逆"軌道"になるが正解でしたー。
       sin(x) = -sin(-x) ですから当然ですね。
       目で見るために倍速回転にしております。'''

def _rotating_square_around_origin_11(passed_seconds):
    '''お遊びでお送りしております。'''
    ps = passed_seconds
    put_on_square(-2 * ps, math.cos(2*ps) * 3 / 8, math.sin(ps) * 8 / 8,
                   0.1, YELLOW)

def _rotating_square_around_origin_12(passed_seconds):
    '''お遊びでお送りしております。'''
    ps = passed_seconds
    put_on_square(-2 * ps, math.cos(2*ps) * 3 / 8, math.sin(-2*ps) * 8 / 8,
                   0.1, RED)

def _rotating_square_around_origin_13(passed_seconds):
    '''お遊びでお送りしております。'''
    '''こいつが一番好きだ。'''
    ps = passed_seconds
    put_on_square(-2 * ps, math.cos(ps) * 3 / 8, math.sin(2*ps) * 8 / 8,
                   0.05, BLUE)

def _rotating_square_around_origin_14(passed_seconds):
    '''お遊びでお送りしております。'''
    ps = passed_seconds
    put_on_square(0, math.cos(ps), 0, 0.05, GREEN)

def _rotating_square_around_origin_15(passed_seconds):
    '''お遊びでお送りしております。'''
    ps = passed_seconds
    put_on_square(0, 0, math.sin(ps), 0.05, GREEN)

def _rotating_square_around_origin_16(passed_seconds):
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

def _rotating_square_on_origin(passed_seconds):
    '''白四角形が、原点上を時計回りでくるくる回る。'''
    put_on_square(-passed_seconds, 0, 0, 0.1)
