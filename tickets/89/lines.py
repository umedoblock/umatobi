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

  # d4 = ((total_slots - redundancy) / redundancy) / (4 * (rate - 1))
  # x4 = np.arange(1, rate + d4, d4)
  # y4 = x4 * 0.0 + 0.20
  # plt.plot(x4, y4, 'go')

  # d5 = ((total_slots - redundancy) / redundancy) / (8 * (rate - 1))
  # x5 = np.arange(1, rate + d5, d5)
  # y5 = x5 * 0.0 + 0.40
  # plt.plot(x5, y5, 'gs')

  # d6 = ((total_slots - redundancy) / redundancy) / (16 * (rate - 1))
  # x6 = np.arange(1, rate + d6, d6)
  # y6 = x6 * 0.0 + 0.60
  # plt.plot(x6, y6, 'gs')

    n_parities = (4, 8, 16)
    count = 0.2
    for n_parity in n_parities:
        d7 = ((total_slots - redundancy) / redundancy) / (n_parity * (rate - 1))
        x7 = np.arange(1, rate + d7, d7)
        y7 = x7 * 0.0 + count
        plt.plot(x7, y7, 'go')
        count += 0.2

    count = 0.3
    for n_parity in n_parities:
        step = ((total_slots - redundancy)) / (n_parity * (rate - 1))
        x8 = np.arange(redundancy, total_slots + 1, step)
        y8 = x8 * 0.0 + count
      # print('x8 =', list(x8))
        x8 /= redundancy
        plt.plot(x8, y8, 'rs')
      # print('x8 =', list(x8))
      # print()
        count += 0.2

    # 縦横の縮尺を同じにする。
    plt.axis('scaled')
    plt.xlim(xmin=1-0.05, xmax=rate+0.05)
    plt.ylim(ymin=-0.05, ymax=1.05)
    plt.grid(True)

    plt.show()
