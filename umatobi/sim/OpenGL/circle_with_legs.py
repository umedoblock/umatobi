import math
import datetime

try:
  from OpenGL.GLUT import *
  from OpenGL.GL import *
  from OpenGL.GLU import *
except:
  print('''
ERROR: PyOpenGL not installed properly.
        ''')
  sys.exit()

def glutBitmapCharacters(font, ss):
  # print('ord(j) =', ord('j'))
  # print('s =', ss)
    for c in ss:
      # print('c =', c)
        ch = ord(c)
        glutBitmapCharacter(font, ch)

def display():
    global frames

    glClearColor(0, 0, 0, 0)
    # 以下の一行は重要
    glClear(GL_COLOR_BUFFER_BIT)

    n = 200 # 200 個の点
    L = [] # 点の配置場所を tuple(ix, iy として格納

    # 点を円形に配置
    # 点の配置場所を計算
    for i in range(n):
        rate = i / n
        rad = 2 * math.pi * rate
        iy = math.sin(rad) * 0.99
        ix = math.cos(rad) * 0.99
        rxy = (rad, ix, iy)
        L.append(rxy)
    # 点を描画
    glPointSize(3)
    glBegin(GL_POINTS)
    glColor3ub(0xff, 0xff, 0xff);
    for rxy in L:
        rad, ix, iy = rxy
        glVertex2f(ix, iy)
    glEnd()

    moving = fmove()
    glBegin(GL_LINES)
    for rxy in L:
        rx, ry, gx, gy = moving_legs(rxy, moving)
        rad, ix, iy = rxy
        # 赤足
        glColor3ub(0xff, 0x00, 0x00);
        glVertex2f(ix, iy)
        glVertex2f(rx, ry)
        # 緑足
        glColor3ub(0x00, 0xff, 0x00);
        glVertex2f(ix, iy)
        glVertex2f(gx, gy)
    glEnd()

    glFlush()
    d = datetime.datetime.today()
    print('\r{}, {:.6f}'.format(d, moving), end='')

    frames += 1

    # 地味だけど、重要
    glutSwapBuffers()

def moving_legs(rxy, moving):
    leg = 0.02
    pai_1_2 = math.pi / 2

    rad, ix, iy = rxy

    thetaR = pai_1_2 + rad - moving
    rx = ix - leg * math.cos(thetaR)
    ry = iy - leg * math.sin(thetaR)

    thetaG = pai_1_2 + math.pi + rad + moving
    gx = ix - leg * math.cos(thetaG)
    gy = iy - leg * math.sin(thetaG)

    return rx, ry, gx, gy

def fmove():
    t = passed_time()

    d, m = divmod(t, 2.0)
    t = m - 1.0
    t = abs(t)
    move = t * (math.pi / 4.0)
    return move

def passed_time():
    e = datetime.datetime.today()
    return (e - s).total_seconds()

def keyboard(key, x, y):
    code = ord(key)
    print()
    print('key={}, x={}, y={}, code={}'.format(key, x, y, code))
    if key.decode() == chr(27):
        print('ESC')
    if ord(key) == 27:
        # 'ESC'

        passed_seconds = passed_time()
        print('passed_seconds =', passed_seconds)
        fps = frames / passed_seconds
        print('fps =', fps)

        sys.exit(0)

frames = 0

s = datetime.datetime.today()

pixel = 500
width = height = pixel
glutInit(sys.argv)
mode = GLUT_SINGLE | GLUT_RGBA
# multi buffering
mode |= GLUT_DOUBLE
glutInitDisplayMode(mode)
glutInitWindowSize(width, height)
glutInitWindowPosition(0, 0)
glutCreateWindow(sys.argv[0].encode())
# init()
glutDisplayFunc(display)
glutIdleFunc(glutPostRedisplay)
# glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutMainLoop()
