import datetime

def stop_watch(func, args, message):
    s = datetime.datetime.now()
    ret = func(*args)
    e = datetime.datetime.now()
    t = (e - s).total_seconds()

    if True:
        print('{:>28s} の処理にかかった時間:'.format(message))
        print('{:.3f}'.format(t))
        print()
    else:
        print('{:>28s} の処理にかかった時間: {:.3f}'.format(message, t))
    return ret

def log_now():
    now = datetime.datetime.now()
    return now.strftime('%Y%m%dT%H%M%S')
