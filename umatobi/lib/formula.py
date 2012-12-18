import math
import struct

def _key2rxy(_keyID):
    '''\
    時計を単位円として考えてください。
    時計の9時から3時の方向にx軸を引き、
    時計の6時から12時の方向にy軸を引いてください。
    key の値は0時をゼロとし、時計回り順で、
    12時(最大値:fff...fff)まで増加することを思い出してください。

    radの意味を理解しにくいかもしれません。
    理解しなくて良いですが、簡単には、
    rad = 2 * PAI  * (今何時？ / 12.0)
    です。
    '''
    norm_rad = (2.0 * math.pi) * (_keyID / 4294967296)

    cs =  math.cos(norm_rad + (3.0 * math.pi / 2.0 ))
    sn = -math.sin(norm_rad + (3.0 * math.pi / 2.0 ))

    m = 1.00
    _x = cs * m
    _y = sn * m

    return norm_rad, _x, _y

def _key_hex(key):
    'key を16進で表現する。'
    fmt = '>' + 'I' * (len(key) // 4)
    hexes = struct.unpack(fmt, key)
    hex_strs = ['{:08x}'.format(hex_) for hex_ in hexes]
    return '0x' + ''.join(hex_strs)

def _moving_legs(rxy, moving, leg=0.033):
    '''\
    赤・緑足の具体的な位置を計算。
    つま先の移動先を計算と言えば分かりやすいか。
    '''
    pai_1_2 = math.pi / 2

    rad, ix, iy = rxy

    thetaR = pai_1_2 + rad - moving
    rx = ix - leg * math.cos(thetaR)
    ry = iy - leg * math.sin(thetaR)

    thetaG = pai_1_2 + math.pi + rad + moving
    gx = ix - leg * math.cos(thetaG)
    gy = iy - leg * math.sin(thetaG)

    return rx, ry, gx, gy

def _fmove(passed_seconds):
    '''\
    0〜1秒: 0からPI/4を移動。
    1〜2秒: PI/4から0まで戻る。
    2秒周期で足を振るよ。って事です。
    '''
    d, m = divmod(passed_seconds, 2.0)
    t = m - 1.0
    t = abs(t)
    move = t * (math.pi / 4.0)
    return move
