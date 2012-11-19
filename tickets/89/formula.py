import math
def combination(n, m):
    'nCm'
    return math.factorial(n) // math.factorial(n - m) // math.factorial(m)

def p_multiplex(send_slots, n_slots, ps):
  # print('p_multiplex(send_slots={}, n_slots={}, ps={})'.format(send_slots, n_slots, ps))
    n, twice = divmod(send_slots, n_slots)
    once = n_slots - twice
    p2 = (1 - (1 - ps) ** (n + 1)) ** twice
    p1 = (1 - (1 - ps) ** n) ** once
    pd = p2 * p1
  # print('n={}, twice={}, once={}'.format(n, twice, once))
  # print('pd={:.3f}, p2={:.3f}, p1={:.3f}'.format(pd, p2, p1))
    return pd

def p_reed_solomon(n, a, ps):
    p = 0.0
    na = n + a
    for k in range(n, na + 1):
        p_success = ps ** k
        p_fail = (1 - ps) ** (na - k)
        p += combination(na, k) * p_success * p_fail
    return p
