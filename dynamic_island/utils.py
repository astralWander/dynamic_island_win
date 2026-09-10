def clamp(t, lo=0.0, hi=1.0):
    return lo if t < lo else (hi if t > hi else t)


def lerp(a, b, t):
    return a + (b - a) * t
