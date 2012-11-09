class Setting(object):
    def __init__(self, args, conf, attrs):
        # 優先順位は args の方が高い。
        # よって、conf, args 両方に設定値があった場合、
        # 後の args の方で上書きする。
        self._setattr(conf, attrs)
        self._setattr(args, attrs)

        for attr in attrs:
            if getattr(self, attr) is None:
                RuntimeError('unknown attr "{}" in attrs "{}".'.format(attr, attrs))
    def _setattr(self, resource, attrs):
        for attr in attrs:
            if hasattr(resource, attr):
                value = getattr(resource, attr)
            else:
                value = None
            setattr(self, attr, value)
