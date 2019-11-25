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

dived = (4, 8, 16, 32)
point_styles = ['o', '*', 's', '+']

data_size = 128 * 1024 ** 2
n_split = 1
slot_size = data_size // n_split
block_size = 1024
n_blocks = slot_size // block_size

slot_size = 128

confidence_on_udp = 0.99
n_is_are = []

print('confidence_on_udp =', confidence_on_udp)
for i, n in enumerate(dived):
    # 多重化
    n_is = '$n={}$'.format(n)
    n_is_are.append(n_is)
    d = 1 / n
    x = np.arange(1.0, 2.0 + d, d)
    n_blocks = slot_size // n
    Ps = confidence_on_udp ** n_blocks
    print('Ps = {:.3f}, n = {}'.format(Ps, n))
    y = theory_multiplex(n, Ps)
    plt.plot(x, y, 'g{}'.format(point_styles[i]))

multiplex = '$Pm=P_o^{n-i}*P_{oo}^{i}$'
plt.text(1.755, 0.13, multiplex, size=16, color='g')

plt.legend(n_is_are, loc='upper left')

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
