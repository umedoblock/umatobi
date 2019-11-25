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

def theory_multiplex(n, Ps):
    Po = Ps
    Poo = 1 - (1 - Ps) ** 2

    Pm = []
    for i in range(n + 1):
        P = Po ** (n - i) * Poo ** i
        Pm.append(P)

    return Pm

    rate = int(rate * 10) / 10
    return rate - 1.0
    '分割のみ、parity無しの場合: 送信成功率を赤色で表示。'
    #  (1 - (1 - p) ** 2) ** n
    return  (p * (2 - p)) ** n

def _P_reed_solomon(n, m, Ps):
    P = 0.0
    for k in range(n, m + 1):
        p_success = Ps ** k
        p_fail = (1 - Ps) ** (m - k)
#       print('p_success = Ps={} ** {}'.format(Ps, k))
#       print('p_fail = (1 - Ps)={:.3f} ** {}(={} - {})'.format(1 - Ps, m - k, m, k))
        P += combination(m, k) * p_success * p_fail
    return P

def _Pr_plus_1(n, Ps):
    Pr1 = combination(2 * n - 1, n - 1) * \
          (Ps ** (n - 1)) * (1 - Ps) ** (2 * n - 1 - (n - 1))
    Pr2 = Ps
    return Pr1 * Pr2

def theory_reed_solomon(n, Ps):
    Pr = []
    P = 0.0
    for m in range(n, 2 * n - 1 + 1):
        P = _P_reed_solomon(n, m, Ps)
      # print('P =', P, 'i =', i)
        Pr.append(P)
    _P = _Pr_plus_1(n, Ps)
    print('_P =', _P)
    Pr.append(P + _P)
    print('--')
    return Pr

dived = (4, 8, 16, 32)
dived = (8, 16)
dived = (8, 16, 32)
point_styles = ['o', 'D', 's', '+']

data_size = 128 * 1024 ** 2
n_split = 1
slot_size = data_size // n_split
block_size = 1024
n_blocks = slot_size // block_size

slot_size = 128

confidence_on_udp = 0.99
n_is_are = []

print('confidence_on_udp =', confidence_on_udp)
print()
for i in range(len(dived)):
    plt.plot([], [], 'k{}'.format(point_styles[i]))
for i, n in enumerate(dived):
    print('=' * 79)
    # 多重化
    n_is = '$n={}$'.format(n)
    n_is_are.append(n_is)
    d = 1 / n
    x = np.arange(1.0, 2.0 + d, d)
    print('len(x) =', len(x))
    n_blocks = slot_size // n
    Ps = confidence_on_udp ** n_blocks

    print('Ps = {:.3f}, n = {}'.format(Ps, n))
    print('n_blocks =', n_blocks)
    y = theory_multiplex(n, Ps)
    plt.plot(x, y, 'g{}'.format(point_styles[i]))

    y = theory_reed_solomon(n, Ps)
    print('Pr =', y)
    plt.plot(x, y, 'b{}'.format(point_styles[i]))
    print()

multiplex = '$Pm=P_o^{n-i}*P_{oo}^{i}$'
multiplex = '$multiplex$'
plt.text(1.73, 0.23, multiplex, size=16, color='g')
reed_solomon = '$reed\_solomon$'
plt.text(1.73, 0.33, reed_solomon, size=16, color='b')

plt.legend(n_is_are, loc='lower right')

# 縦横の縮尺を同じにする。
plt.axis('scaled')
plt.xlim(xmin=0.95, xmax=2.05)
plt.ylim(ymin=-0.05, ymax=1.05)
plt.grid(True)

fprop = fm.FontProperties(fname='/usr/share/fonts/truetype/mona/mona.ttf')
plt.title('reed solomon の有効性について', fontproperties=fprop)
plt.xlabel('送信data率', fontproperties=fprop)
plt.ylabel('slot を data に復元できる成功率', fontproperties=fprop)
plt.minorticks_off()   # 補助目盛りを表示しない
plt.locator_params(axis='both', tight=False, nbins=21) # grid 間隔

plt.show()
