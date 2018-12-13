import math
import struct
import os

# norm means normalize, not normal.

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

    norm_rad = keyID_to_norm_rad(_keyID)
    math_rad = _norm_rad_to_math_rad(norm_rad)
    cs = math.cos(math_rad)
    sn = math.sin(math_rad)

    m = 1.00
    _x = cs * m
    _y = sn * m

    return norm_rad, _x, _y

def get_current_cos_sin_in_window(ww, wh, x, y):
    rate = ww / wh
    # math x, y axis
    # origin is window center
    # -ww / 2 <= x <= ww / 2
    # -wh / 2 <= y <= wh / 2
    mx = x - ww / 2
    my = wh / 2 - y

    # normalize
    norm_ww = ww / 2
    norm_wh = wh / 2 * rate
    norm_wd = math.sqrt(norm_ww ** 2 + norm_wh ** 2)
    norm_x = int(mx)
    norm_y = int(my * rate)
    norm_d = math.sqrt(norm_x ** 2 + norm_y ** 2)
    if norm_d == 0:
        return None, None, 0
    cos_ = norm_x / norm_d
    sin_ = norm_y / norm_d

    r = norm_ww
    # clickした箇所と原点(=単位円の中心)からの距離
    distance_of_click_on_from_origin = norm_d / r
    docofo = distance_of_click_on_from_origin

    return cos_, sin_, docofo

def cos_sin_to_norm_rad(cs, sn):
    if sn >= 0:
        math_rad = math.acos(cs)
    else:
        math_rad = 2 * math.pi - math.acos(cs)
    norm_rad = _math_rad_to_norm_rad(math_rad)
    return norm_rad

def keyID_to_norm_rad(keyID):
    rate = keyID / (1 << 32)
    norm_rad = (2 * math.pi) * rate
    return norm_rad

def norm_rad_to_keyID(norm_rad):
    rate = norm_rad / (2 * math.pi)
    keyID = int((1 << 32) * rate)
    return keyID

def _math_rad_to_norm_rad(math_rad):
    norm_rad = -math_rad + math.pi / 2.0
    if norm_rad < 0:
        norm_rad += 2 * math.pi
    if norm_rad > 2 * math.pi:
        norm_rad -= 2 * math.pi
    return norm_rad

def _norm_rad_to_math_rad(norm_rad):
    math_rad = -norm_rad + math.pi / 2.0
    if math_rad < 0:
        math_rad += 2 * math.pi
    if math_rad > 2 * math.pi:
        math_rad -= 2 * math.pi
    return math_rad

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

if __name__ == '__main__':
    expected = '''\
        keyID=0x00000000, rxy=(0.000,0.000,1.000)
        keyID=0x10000000, rxy=(0.393,0.383,0.924)
        keyID=0x20000000, rxy=(0.785,0.707,0.707)
        keyID=0x30000000, rxy=(1.178,0.924,0.383)
        keyID=0x40000000, rxy=(1.571,1.000,0.000)
        keyID=0x50000000, rxy=(1.963,0.924,-0.383)
        keyID=0x60000000, rxy=(2.356,0.707,-0.707)
        keyID=0x70000000, rxy=(2.749,0.383,-0.924)
        keyID=0x80000000, rxy=(3.142,-0.000,-1.000)
        keyID=0x90000000, rxy=(3.534,-0.383,-0.924)
        keyID=0xa0000000, rxy=(3.927,-0.707,-0.707)
        keyID=0xb0000000, rxy=(4.320,-0.924,-0.383)
        keyID=0xc0000000, rxy=(4.712,-1.000,0.000)
        keyID=0xd0000000, rxy=(5.105,-0.924,0.383)
        keyID=0xe0000000, rxy=(5.498,-0.707,0.707)
        keyID=0xf0000000, rxy=(5.890,-0.383,0.924)'''
    expects = [s.strip() for s in expected.split('\n')]

    fail = False
    i = 0
    for keyID in range(0, 1 << 32, 0x10000000):
        rxy = _key2rxy(keyID)
        rxy_s = '({})'.format(','.join(['{:.3f}'.format(xx) for xx in rxy]))
        message = 'keyID=0x{:08x}, rxy={}'.format(keyID, rxy_s)
        if expects[i] != message:
            print('expectes =', expects[i])
            print(' message =', message)
            print()
            fail = True
        i += 1
    if not fail:
        print('test success.')
