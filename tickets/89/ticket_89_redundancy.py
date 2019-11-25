# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

# UDPで信頼できる通信を行う際に、reed solomonが有効か確認する。
import math

# 参考: http://w.livedoor.jp/met-python/d/matplotlib
import numpy as np
import matplotlib.pyplot as plt
# 参考: http://matplotlib.org/api/font_manager_api.html
#     : http://akebononotsumiki.halfmoon.jp/?matplotlib
import matplotlib.font_manager as fm

def combination(n, m):
    'nCm'
    return math.factorial(n) // math.factorial(n - m) // math.factorial(m)
# for n, m in [(4, 2), (6, 2), (7, 3)]:
#     print('{}C{} = {}'.format(n, m, combination(n, m)))
# 4C2 = 6
# 6C2 = 15
# 7C3 = 35

def _P_reed_solomon(redundancy, prities, Ps):
    P = 0.0
    for k in range(redundancy, redundancy + prities + 1):
        p_success = Ps ** k
        p_fail = (1 - Ps) ** (redundancy + prities - k)
        P += combination(redundancy + prities, k) * p_success * p_fail
    return P

def _Pr_plus_1(n, Ps):
    Pr1 = combination(2 * n - 1, n - 1) * \
          (Ps ** (n - 1)) * (1 - Ps) ** (2 * n - 1 - (n - 1))
    Pr2 = Ps
    return Pr1 * Pr2

def theory_reed_solomon(redundancy, n_parity, Ps):
    Pr = []
    P = 0.0
    P = _P_reed_solomon(redundancy, n_parity, Ps)
    print('(redundancy={}, n_parity={}, Ps={}, P={})'.format(redundancy, n_parity, Ps, P))
    return P
#   for m in range(redundancy, redundancy + n_parity + 1):
#       P = _P_reed_solomon(redundancy, m, Ps)
#     # print('P =', P, 'i =', i)
#       Pr.append(P)
#   _P = _Pr_plus_1(redundancy, Ps)
    print('_P =', _P)
    _P = 1.00
    Pr.append(P + _P)
    print('--')
    return Pr

axes = plt.subplot(111)
axes.set_xscale("log", basex=2)

data_size = 128 * 1024 ** 2
n_split = 1
slot_size = data_size // n_split
block_size = 1024
n_blocks = slot_size // block_size

n_parities = [0, 1, 2, 3]
point_styles = ['o', 'D', 's', '+']
if len(n_parities) != len(point_styles):
    raise RuntimeError('len(n_parities={}) != len(point_styles={})'.format(n_parities, point_styles))

slot_size = 128

confidence_on_udp = 0.99
n_parity_is_are = []

print('confidence_on_udp =', confidence_on_udp)
print()
for i in range(len(n_parities)):
    plt.plot([], [], 'k{}'.format(point_styles[i]))

n_redundancy = 64
n_redundancy = 32
i = 0
x = np.arange(1, n_redundancy + 1)
x = [2, 4, 8, 16, 32, 64, 128]
for n_parity in n_parities:
    print('=' * 79)
    y = []
    redundancies = x
    n_parity_is = '$n\_parity\_is={}$'.format(n_parity)
    n_parity_is_are.insert(0, n_parity_is)
    for redundancy in redundancies:
        n_blocks = slot_size // redundancy
        print('n_blocks={}'.format(n_blocks))
        Ps = confidence_on_udp ** n_blocks

        #   n_parity: 固定
        # redundancy: 毎回変更
        P = theory_reed_solomon(redundancy, n_parity, Ps)
        y.append(P)
    print('y =', y)

    plt.plot(x, y, 'b{}'.format(point_styles[i]))
    print()
    i += 1

reed_solomon = '$reed\_solomon$'
plt.text(1.73, 0.33, reed_solomon, size=16, color='b')

plt.legend(n_parity_is_are, loc='lower right')

# 縦横の縮尺を自動的にどうにかしてもらう。
plt.axis('auto')
plt.xlim(xmin=0, xmax=max(x) * 2)
plt.ylim(ymin=-0.05, ymax=1.05)
plt.grid(True)

fprop = fm.FontProperties(fname='/usr/share/fonts/truetype/mona/mona.ttf')
plt.title('reed solomon の有効性について', fontproperties=fprop)
plt.xlabel('redundancy 分割数', fontproperties=fprop)
plt.ylabel('slot を data に復元できる成功率', fontproperties=fprop)
plt.minorticks_off()   # 補助目盛りを表示しない
# plt.locator_params(axis='both', tight=False, nbins=21) # grid 間隔

plt.show()
