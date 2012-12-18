import math

# norm means normalize, not normal.

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

def cos_sin_to_norm_rad(cs, sn):
    if sn >= 0:
        math_rad = math.acos(cs)
    else:
        math_rad = 2 * math.pi - math.acos(cs)
    return _math_rad_to_norm_rad(math_rad)

def norm_rad_to_keyID(norm_rad):
    rate = norm_rad / (2 * math.pi)
    return int((1 << 32) * rate)
### rate = norm_rad / (2 * math.pi)
### return int((1 << 32) * norm_rad / (2 * math.pi))

def _keyID_to_norm_rad(keyID):
    rate = keyID / (1 << 32)
    norm_rad = 2 * math.pi * rate
    return norm_rad

if __name__ == '__main__':

    half_pi = math.pi / 2
    for i in range(4):
        n_half_pi = half_pi * i
        print('{} / 2 * pi = {:.3f}'.format(i, n_half_pi))
    print('--')

    pairs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    for cs, sn in pairs:
        rd = cos_sin_to_norm_rad(cs, sn)
        print('cs={:.3f}, sn={:.3f}, rd={:.3f}, n = {:.3f}'.format(cs, sn, rd, rd / math.pi))
    print('--')

    print('math_rad is 0 to 2 * pi, cos(math_rad), sin(math_rad), in math')
    pairs = []
    n = 16
    step = 2 * math.pi / n
    for i in range(n):
        math_rad = step * i
        cs = math.cos(math_rad)
        sn = math.sin(math_rad)
        norm_rad = cos_sin_to_norm_rad(cs, sn)
        _math_rad = _norm_rad_to_math_rad(norm_rad)
        d_rad = math.fabs(math_rad - _math_rad)
        if math_rad != _math_rad and d_rad >= 0.000001:
            tup = ('', 'math_rad={} not equal to ',
                   '_math_rad={}, ', 'norm_rad={:.3f}', 'd={}')
            fmt = '\n'.join(tup)
          # >>> sys.float_info
          # sys.float_info(max=1.7976931348623157e+308, max_exp=1024,
          # max_10_exp=308, min=2.2250738585072014e-308, min_exp=-1021,
          # min_10_exp=-307, dig=15, mant_dig=53, epsilon=2.220446049250313e-16,
          # radix=2, rounds=1)
            raise RuntimeError(fmt.format(math_rad, _math_rad, norm_rad, d))
        pairs.append((norm_rad, cs, sn))
    pairs.sort(key=lambda x: x[0])

    i = 0
    for norm_rad, cs, sn in pairs:
        keyID = norm_rad_to_keyID(norm_rad)
        print('cs={:.3f}, sn={:.3f}, keyID=0x{:08x}, norm_rd={:.3f}, n = {:.3f}'.format(cs, sn, keyID, norm_rad, norm_rad / math.pi))
        i += 1
        if i % (len(pairs) // 4) == 0:
            print()
