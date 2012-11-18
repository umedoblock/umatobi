import sys

# 参考: http://w.livedoor.jp/met-python/d/matplotlib
import numpy as np
import matplotlib.pyplot as plt

import formula

if __name__ == '__main__':
    if len(sys.argv) < 2:
        rate = 2
    else:
        rate = int(sys.argv[1])
    print('rate =', rate)
    print()

    # n_blocks * block = slot
    # n_slots  * slot  = data
    # n_blocks * n_slots * block = data
    # n_slots = redundancy
    # data_blocks = n_slots * n_blocks
    data_blocks = 128
    pb = 0.99

    total_blocks = data_blocks * rate
    xt = np.arange(data_blocks, rate * data_blocks + 1.0)
    yt = []
    for x in xt:
        p = pb ** x
        p = formula.p_multiplex(int(x), int(data_blocks), pb)
        yt.append(p)
    xt /= data_blocks
    plt.plot(xt, yt, color='k', lw=1)

    n_slots_tup = (8, 16, 32)
    for n_slots in n_slots_tup:
        n_blocks = data_blocks // n_slots
        ps = pb ** n_blocks
        print('n_blocks={}'.format(n_blocks))
        print('n_slots={}'.format(n_slots))
        print('pb={:.3f}'.format(pb))
        print('ps={:.3f}'.format(ps))

        xs = np.arange(n_slots, n_slots * rate + 1.0)
        ys = []
        for x in xs:
            pd = formula.p_multiplex(int(x), int(n_slots), ps)
            ys.append(pd)
        xs /= n_slots
        plt.plot(xs, ys, 'g.')
      # print('xs =', list(xs))
      # print('ys =', list(ys))
        print()

    # 縦横の縮尺を同じにする。
    plt.axis('scaled')
    plt.xlim(xmin=1-0.05, xmax=rate+0.05)
    plt.ylim(ymin=-0.05, ymax=1.05)
    plt.grid(True)

    # from ticket_89.py
    plt.minorticks_on()
    plt.locator_params(axis='both', tight=False, nbins=21) # grid 間隔
    plt.show()
