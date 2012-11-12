# UDPで信頼できる通信を行う際に、reed solomonが有効か確認する。
# 参考: http://w.livedoor.jp/met-python/d/matplotlib
import numpy as np
import matplotlib.pyplot as plt

x1 = np.arange(0, 1, 0.01)
y1 = np.exp(x1)
plt.plot(x1, y1, linewidth=1.0)

x2 = np.arange(0, 1, 0.1)
y2 = np.exp(x2)
# dot
plt.plot(x2, y2, 'ro')

x3 = np.arange(0, 1, 0.33)
y3 = x3
# dot
plt.plot(x3, y3, 'o', color='b')

x4 = np.arange(-1, np.sqrt(7), 0.001)
y4 = - (x4 ** 2) + 6
plt.plot(x4, y4, linewidth=1)

x5 = np.arange(0, 4, 0.01)
y5 = (x5 ** 2)
plt.plot(x5, y5, linewidth=1, color='y')

x6 = np.arange(-1, 9, 0.01)
y6 = -(x6 - 5) ** 2 + 7
plt.plot(x6, y6, linewidth=1, color='k')

'''
matplotlib/colors.py
def to_rgb(self, arg):
    """
    Returns an *RGB* tuple of three floats from 0-1.

    *arg* can be an *RGB* or *RGBA* sequence or a string in any of
    several forms:

        1) a letter from the set 'rgbcmykw'
        2) a hex color string, like '#00FFFF'
        3) a standard name, like 'aqua'
        4) a float, like '0.4', indicating gray on a 0-1 scale

    if *arg* is *RGBA*, the *A* will simply be discarded.
    """
    ...
'''

# x_range = (-1, 3)
# y_range = (-1, 3)
# plt.axis(x_range + y_range)

# 縦横の縮尺を同じにする。
plt.axis('scaled')
plt.xlim(xmin=-1, xmax=9)
plt.ylim(ymin=-1, ymax=9)
# plt.xticks(0.5)
plt.grid(True)

plt.title('title: example-pyplot.py')
plt.xlabel('x: describe label of x')
plt.ylabel('y: describe label of y')

# grid 間隔
# plt.locator_params(axis='x', tight=True, nbins=18)
# plt.locator_params(axis='y', tight=True, nbins=18)
# plt.locator_params(axis='x', tight=False, nbins=18)
# plt.locator_params(axis='y', tight=False, nbins=18)
plt.locator_params(axis='both', tight=False, nbins=18)
plt.locator_params(axis='both', tight=False, nbins=18)

# print(dir(plt))
plt.minorticks_off()   # 補助目盛りを表示しない
plt.minorticks_on()   # 補助目盛りを表示する

plt.show()
