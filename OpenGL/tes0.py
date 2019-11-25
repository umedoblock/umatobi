# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi


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
    pointSize = 4

    glClear(GL_COLOR_BUFFER_BIT)

    glPointSize(pointSize)
    glBegin(GL_POINTS)
    glVertex2f(0 , -0.9)
    glEnd()

    # 画面ど真ん中に色々表示。
    glRasterPos2f(0.0, 0.0)
    glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord('a'))
    glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord('b'))
    glutBitmapCharacter(GLUT_STROKE_ROMAN, ord('c')) # not found
    glutBitmapCharacter(GLUT_STROKE_MONO_ROMAN, ord('d')) # not found
    glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord('e'))
    glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord('f'))
    glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_10, ord('g'))
    glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord('h'))
    glutBitmapCharacter(GLUT_BITMAP_HELVETICA_10, ord('i'))
    glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord('j'))
    glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord('k'))
    glutBitmapCharacters(GLUT_BITMAP_HELVETICA_18, 'LMN')

    glPointSize(pointSize*2)
    glBegin(GL_POINTS)
    glVertex2f(-0.9 , 0.9)
    glEnd()

    glPointSize(pointSize*4)
    glBegin(GL_POINTS)
    glVertex2f(0.9 , 0.9)
    glEnd()

    glFlush()

def keyboard(key, x, y):
    code = ord(key)
    print('key={}, x={}, y={}, code={}'.format(key, x, y, code))
    if key.decode() == chr(27):
        print('ESC')
    if ord(key) == 27:
        # 'ESC'
        sys.exit(0)

num = 500
width = height = num
glutInit(sys.argv)
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
glutInitWindowSize(width, height)
glutInitWindowPosition(0, 0)
glutCreateWindow(b'tes0')
# init()
glutDisplayFunc(display)
# glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutMainLoop()
