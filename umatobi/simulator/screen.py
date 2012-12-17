import datetime
import sys
import math
import pickle
import threading
import tkinter as tk

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib.args import args_make_simulation_db
import simulator.sql
from lib import formula
from lib.squares import put_on_square
from tools.make_simulation_db import init_nodes_table

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
    def __init__(self, argv, width=500, height=500):
        self.frames = 0
        self.s = datetime.datetime.now()
        self._last_select_milliseconds = 0
        self.width = width
        self.height = height
        self.mode = GLUT_SINGLE | GLUT_RGBA
        # multi buffering
        self.mode |= GLUT_DOUBLE
        self.nodes = []

        self.label_area = LabelArea()

        glutInit(argv)
        glutInitDisplayMode(self.mode)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(0, 0)
        glutCreateWindow(argv[0].encode())

        glutDisplayFunc(self._display)
        glutIdleFunc(glutPostRedisplay)
        glutKeyboardFunc(self._keyboard)
        glutMouseFunc(self._mouse)

    def set_display(self, display_main):
        self.display_main = display_main

    def set_db(self, db):
        self._db = db
        self._db.access_db()
        init_nodes_table(self._db)
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

    def _print_fps(self):
        ps = self._passed_time()
        fps = self.frames / ps
        print('frames =', self.frames)
        print('passed_seconds = {:.3f}'.format(ps))
        print('fps = {:.3f}'.format(fps))

    def _simulation_info(self):
        print('\n')
        self._print_fps()
      # print(dir(self.label_area.tk_root))
        print('display =', self.label_area.display)
        print('display.master =', self.label_area.display.master)
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
            print('count={}, th={}'.format(count, th))
            count += 1

#   def _mouse(self, *event):
#       print('event={} in self._mouse()'.format(event))
    def _mouse(self, button, state, x, y):
      # 左click 押した button=0, state=0, x=392, y=251  in self._mouse()
      # 左click 離した button=0, state=1, x=392, y=251  in self._mouse()

        fmt = 'button={}, state={}, x={}, y={}  in self._mouse()'
        print(fmt.format(button, state, x, y))

    def _keyboard(self, key, x, y):
        code = ord(key)
        print()
        print('key={}, x={}, y={}, code={}'.format(key, x, y, code))
        if key.decode() == chr(27):
            print('ESC')
        if ord(key) == 27 or ord(key) == 0x17 or ord(key) == 0x03:
          # ESC              ctr-w               ctr-c
          # self.label_area._tk_root.destroy()
          # self.label_area.done()
            self._simulation_info()
          # self.label_area.display.destroy()
          # self.label_area.display.master.destroy()
            print('_keyboard() do sys.exit(0)')
            sys.exit(0)

    def display_main(self, passed_seconds):
        milliseconds = _normalize_milliseconds(passed_seconds)
#       print('\rmilliseconds = {:7d}'.format(milliseconds), end='')
        s = milliseconds - 1000
        if s < 0:
            s = 0
        if s > self.simulation_milliseconds:
            self._simulation_info()
            sys.exit(0)
        e = milliseconds

        conditions = \
            'where elapsed_time >= {} and elapsed_time < {}'. \
             format(self._last_select_milliseconds, e)
        self._last_select_milliseconds = e
        records = self._db.select('growings', 'elapsed_time,pickle',
            conditions=conditions
        )

      # print('conditions =', conditions)
      # print('milliseconds = {}, len(records) = {}'. \
      #        format(milliseconds, len(records)))
        if len(records) >= 1:
            print('conditions={}, len(records)={}'.format(conditions, len(records)))
            for record in records:
                d = pickle.loads(record['pickle'])
                print('elapsed_time={}, d = {}'.format(record['elapsed_time'], d))
                where = {'id': d['id']}
                self._db.update('nodes', d, where)
                self._db.commit()
            print()

        L = []
        len_body = 0.011
        len_leg = 0.033
        nodes = self._db.select('nodes')
        for node in nodes:
            if node['status'] == 'active':
                _keyID = int(node['key'][:10], 16)
                r, x, y = formula._key2rxy(_keyID)
              # print('r, x, y =', r, x, y)
                put_on_square(r, x, y, len_body)
                L.append('id: {}, key: {}'.format(node['id'], node['key']))
        self.label_area.update('\n'.join(L))

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
