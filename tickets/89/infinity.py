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
    max_redundancy = 64

    point_styles = ['o', 'D', 's', '+'] * 2
    index = 0
    for n_parity_slots in range(0, 4 + 1):
        xs = np.arange(1, max_redundancy + 1)
        ys = []
        for x in xs:
            n_slots = x
            if n_slots <= n_parity_slots:
                continue
            if n_slots == 0:
                raise RuntimeError('n_slots must be positive integer.')
            n_blocks = data_blocks / n_slots
            ps = pb ** n_blocks
          # print('n_slots=x={}'.format(x))
          # print('n_blocks={}'.format(n_blocks))
          # print('n_slots={}'.format(n_slots))
          # print('pb={:.3f}'.format(pb))
          # print('ps={:.3f}'.format(ps))
          # print()

            pd = formula.p_reed_solomon(int(n_slots), int(n_parity_slots), ps)
            ys.append(pd)

        xs = xs[len(xs)-len(ys):]
        plt.plot(xs, ys, 'b{}'.format(point_styles[index]))
      # plt.plot(xs, ys, lw=1, color='b')
        index += 1
      # print('len(xs) =', len(xs))
      # print('len(ys) =', len(ys))
      # print('xs =', list(xs))
      # print('ys =', list(ys))
      # print()

    plt.xlim(xmin=0, xmax=max_redundancy+1)
    plt.ylim(ymin=-0.05, ymax=1.05)
    plt.grid(True)

    # from ticket_89.py
    plt.minorticks_on()
    plt.locator_params(axis='both', tight=False, nbins=21) # grid 間隔
    plt.show()
