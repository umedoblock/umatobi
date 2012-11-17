import sys

# 参考: http://w.livedoor.jp/met-python/d/matplotlib
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    if len(sys.argv) < 2:
        rate = 2
    else:
        rate = int(sys.argv[1])
    print('rate =', rate)

    redundancy = 8
    redundancy = 32

    total_slots = redundancy * rate

    plt.subplot('211')
    # (1, 0)から(2, 1)まで青色の直線を引く。
    d1 = (2 - 1) / redundancy
    x1 = np.arange(1, 2 + d1, d1)
    y1 = x1 - 1
    plt.plot(x1, y1, linewidth=1.0, color='b')

    # (1, 0)から(rate, 1)まで赤色の直線を引く。
    d2 = (rate - 1) / redundancy
    x2 = np.arange(1, rate + d2, d2)
    y2 = 1 / (rate - 1) * x2 - 1 / (rate - 1)
    plt.plot(x2, y2, linewidth=1.0, color='r')

    # 縦横の縮尺を同じにする。
    plt.axis('scaled')
    plt.xlim(xmin=1-0.05, xmax=rate+0.05)
    plt.ylim(ymin=-0.05, ymax=1.05)
    plt.grid(True)

    plt.subplot('212')
    # (1, 0)から(rate, 1)まで赤色の直線を引く。
    d3 = ((total_slots - redundancy) / redundancy) / redundancy
    x3 = np.arange(1, rate + d3, d3)
    y3 = 1 / (rate - 1) * x3 - 1 / (rate - 1)
    plt.plot(x3, y3, linewidth=1.0, color='r')

    # 縦横の縮尺を同じにする。
    plt.axis('scaled')
    plt.xlim(xmin=1-0.05, xmax=rate+0.05)
    plt.ylim(ymin=-0.05, ymax=1.05)
    plt.grid(True)

    plt.show()
