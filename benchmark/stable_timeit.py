from timeit import repeat as _repeat
from timeit import default_timer


default_repeat = 100
default_number = 100


def closeness(a1, a2):
    assert len(a1) == len(a2), 'a1,a2 must have the same length'
    return sum((x-y)**2 for x, y in zip(a1, a2))/len(a1)


def stable_timeit(stmt='pass', setup='pass', timer=default_timer,
                  repeat=default_repeat, number=default_number):
    times = []
    for i in range(3):
        t = _repeat(stmt=stmt, setup=setup, timer=timer,
                    repeat=repeat, number=number)
        times.append(t)
    return analyze(times, repeat)


def analyze(times, repeat):
    assert len(times) == 3, 'times must have 3 items'
    # remove 50% noises
    times = [list(sorted(t))[:int(repeat/2)] for t in times]
    L = int(repeat/4)
    # positions
    ns = []
    for t0, t1, t2 in [
        [times[0], times[1], times[2]],
        [times[1], times[2], times[0]],
        [times[2], times[0], times[1]],
    ]:
        # find the middle position of stable datas
        cs = []
        for i in range(L):
            cs.append((closeness(t0[i:i+L], t1[i:i+L]), i))
        ns.append(min(cs)[1]+int(L/2))
    # middle position
    N = int(sum(ns)/3)
    # middle value
    t = sum([t[N] for t in times])/3.0
    return t
