import math

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

    # 以下の一行は重要
    glClear(GL_COLOR_BUFFER_BIT)

    n = 200
    for i in range(n):
        rate = i / n
        point_size = 4 * rate + 1
        glPointSize(point_size)
        glBegin(GL_POINTS)
        rad = 2 * math.pi * rate
        sin = math.sin(rad) * 0.99
        cos = math.cos(rad) * 0.99
        glVertex2f(cos, sin)
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
