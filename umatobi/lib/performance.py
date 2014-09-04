import datetime

def stop_watch(func, **kwargs):
  # print("kwargs = {} in stop_watch()".format(kwargs))
  # print("func =")
    ss = str(func)
  # print(ss)
    func_name = ss.split()[1]
  # print("func_name =")
  # print("{}()".format(func_name))
    s = datetime.datetime.now()
    ret = func(**kwargs)
    e = datetime.datetime.now()
    t = (e - s).total_seconds()

    str_kwargs = ""
    if kwargs:
      # >>> "repr() shows quotes: {!r}; str()
      #      doesn't: {!s}".format('test1', 'test2')
      # "repr() shows quotes: 'test1'; str() doesn't: test2"
      # >>> "hope to {!r} and {!r}".format('test1', 100)
      # "hope to 'test1' and 100"
      # >>> d = {"s": "string", "n": 100}
      # >>> "s={s!r}, n={n!r}".format(**d)
      # "s='string', n=100"
      # >>> d = {"a": 100, "b": 200, "c": "strings"}
      # >>> ", ".join(["{k}={v!r}".format(k=k, v=v) for k, v in d.items()])
      # "b=200, c='strings', a=100"
      # programmar がstop_watch() を呼び出すときに使用した
      # kwargs をそのまま出力したかったので、頑張ってみました。
      # 凝り性ですかね。
        str_kwargs += \
            ", ".join(["{k}={v!r}".format(k=k, v=v) for k, v in kwargs.items()])
    how_to_call = "{0:}({1:})".format(func_name, str_kwargs)
    print('{:>28s} の処理にかかった時間:'.format(how_to_call))
    print('{:.3f}'.format(t))
    print()

    return ret

def log_now():
    now = datetime.datetime.now()
    return now.strftime('%Y%m%dT%H%M%S')
