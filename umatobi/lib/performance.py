import datetime

def stop_watch(func, message):
    s = datetime.datetime.today()
    func()
    e = datetime.datetime.today()
    t = (e - s).total_seconds()

    if True:
        print('{:>28s} の処理にかかった時間:'.format(message))
        print('{:.3f}'.format(t))
        print()
    else:
        print('{:>28s} の処理にかかった時間: {:.3f}'.format(message, t))

def log_now():
    now = datetime.datetime.today()
    return now.strftime('%Y%m%dT%H%M%S')
