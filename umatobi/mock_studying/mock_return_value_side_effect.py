# https://docs.python.org/3/library/unittest.mock-examples.html

import unittest
from unittest.mock import patch

class SomeClass(object):
    attribute = 'someclass_someclass'

    function = 'function'
#   def function(cls):
#       return 'function'

class Sentinel(object):
    attribute = 'sentinel_sentinel'

    def __init__(self):
        self.attr = 'in __init__()'

    def func(self):
        print('in Sentinel.func()')

    def method(self):
        print(self.attr)

    def apple(self):
        return 'aaa'

sentinel = Sentinel()
print('sentinel =', sentinel)

original = SomeClass.attribute
print('original =', original)
print()

@patch.object(SomeClass, 'attribute', sentinel.attribute)
def test():
    print(f'SomeClass.attribute(={SomeClass.attribute}) == sentinel.attribute(={sentinel.attribute})')
    assert SomeClass.attribute == sentinel.attribute

@patch.object(SomeClass, 'function', return_value=sentinel.attribute)
def test2(what):
    print('what =', what)
    print('what() =', what())
    print('what.function() =', what.function())
    print(f'SomeClass.function()(={SomeClass.function()}) == sentinel.attribute={sentinel.attribute})')
    assert SomeClass.function() == sentinel.attribute

test()
print(f'SomeClass.attribute(={SomeClass.attribute}) == original(={original})')
assert SomeClass.attribute == original
print()

test2()
print()

def test_func():
    config = {'method.return_value': 3, 'other.side_effect': KeyError}
    patcher = patch('__main__.Sentinel', **config)
    mock_thing = patcher.start()
    s = Sentinel()
    print('Sentinel.method() =')
    print(Sentinel.method())
    print('s =')
    print(s)
    print('s() =')
    print(s())
    print('s.method() =')
    print(s.method())

    print('mock_thing.method() =')
    print(mock_thing.method())
    print('mock_thing.other() =')
    try:
        mock_thing.other()
    except KeyError as err:
        print('got KeyError()')
    patcher.stop()
    print()

    s = Sentinel()
    patcher = patch.object(s, 'func', return_value='return')
    patcher.start()
    print('s.func() =')
    print(s.func())
    patcher.stop()
    print()

    print('s.method() 1 =')
    s.method()

    patcher = patch.object(s, 'method', return_value='from patch.object')
    patcher.start()
    print('s.method() 2 =')
    print(s.method())
    patcher.stop()
    print()

    patcher = patch.object(s, 'apple', return_value='yes')
    patcher.start()
    print('fruit ? =')
    print(s.apple())
    patcher.stop()
    print()

test_func()
