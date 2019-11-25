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

def theory_multiplex(p, n):
    '分割のみ、parity無しの場合: 送信成功率を赤色で表示。'
    #  (1 - (1 - p) ** 2) ** n
    return  (p * (2 - p)) ** n

#   print('n, m =', n, m)
def theory_reed_solomon(p, n):
    '分割、parityありの場合: 復元に成功する確率を緑色で表示。'
    probabilities = []
    for k in range(n, 2 * n - 1 + 1):
        p_success = p ** k
        p_fail = (1 - p) ** ((2 * n - 1) - k)
        p_total = combination(2 * n - 1, k) * p_success * p_fail
        probabilities.append(p_total)
    P = 0.0
    for i, probability in enumerate(probabilities):
      # print('i = {}, probability = {}'.format(i, probability))
        P += probability
  # print('i = {}, P = {}'.format(i, P))
    return P

d = 0.01
x = np.arange(0, 1 + d, d)

threshold = 0.6
for index, prob in enumerate(x):
    if prob >= threshold:
        break

dived = (32, 16, 8, 4)
x_ = threshold

# 原点から(1, 1)まで青色の直線を引く。
y1 = x
plt.plot(x, y1, linewidth=1.0, color='b')

styles = ['-', ':', '.', ',']
for i, n in enumerate(dived):
    # 多重化
    P = theory_multiplex(x, n)
    plt.plot(x, P, linewidth=1.0, color='r')

    y_ = P[index]
    n_is = '$n={}$'.format(n)
    plt.text(x_, y_, n_is)

    # reed solomon
    P = theory_reed_solomon(x, n)
    plt.plot(x, P, 'g{}'.format(styles[i]), linewidth=1.0)

    y_ = P[index]
    n_is = '$n={}$'.format(n)
    plt.text(x_, y_, n_is)

multiplex = '$[1-(1-p)^2]^n$'
plt.text(0.755, 0.13, multiplex, size=16, color='k')
reed_solomon = '$\Sigma_{k=n}^{2n-1}[_{2n-1}C_k*p^k*(1-p)^{(2n-1)-k}]$'
plt.text(-0.045, 0.73, reed_solomon, size=16, color='k')

plt.legend(('$p$', '$multiplex$', '$reed\ solomon$'), loc='upper left')

# 縦横の縮尺を同じにする。
plt.axis('scaled')
plt.xlim(xmin=-0.05, xmax=1.05)
plt.ylim(ymin=-0.05, ymax=1.05)
plt.grid(True)

fprop = fm.FontProperties(fname='/usr/share/fonts/truetype/mona/mona.ttf')
plt.title('reed solomon の有効性について', fontproperties=fprop)
plt.xlabel('slot 一つを無事に届けられる確率', fontproperties=fprop)
plt.ylabel('slot を data に復元できる成功率', fontproperties=fprop)
plt.minorticks_off()   # 補助目盛りを表示しない
plt.locator_params(axis='both', tight=False, nbins=21) # grid 間隔

plt.show()
