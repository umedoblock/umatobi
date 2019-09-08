import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

class Bar(object):
    def __init__(self):
        self.bar = 'bar __init__()' # __init__() kill bar() function
        print('bar __init__()')

    def bar(self):
      # self.bar = 'bar bar()' # bar() suiside ageint Bar class
        print('bar bar()')

    def baz(self):
        self.baz = 'baz baz()'
        print('bar baz()')
      # self.bar() # bar() is dead.

class Foo(object):
    sock = 'sock'

    def __init__(self):
        self.attr = 100
        self.sock = 'sock in __init__()'

    def sock2(self):
        pass

    def tes(self):
        return 'I am tes().'

if __name__ == '__main__':
    bar = Bar()
  # bar.bar()
    bar.baz()

    print()
    print('hello')
    m = MagicMock()
  # print('mock =', m)

    foo = Foo()
    print()
    with patch.object(foo, 'sock', 'sock with') as mocked1:
        print('foo.sock =', foo.sock)

    print()
    with patch.object(Foo, 'sock2', return_value='sock2() with') as mocked2:
        print('mocked2 =', mocked2)
        foo2 = Foo()
        print('2 foo2.sock2() =', foo2.sock2())
    mocked2.assert_called_once_with()

    print()
    with patch.object(Foo, 'sock2', autospec=True) as mocked3:
        print('mocked3 =', mocked3)
        mocked3.return_value = 'mocked3.return_value'
        foo3 = Foo()
        print('3 foo3.sock2() =', foo3.sock2())
    mocked3.assert_called_once_with(foo3)

    print()
    foo3 = Foo()
    with patch.object(Foo, 'tes') as mocked_tes:
        mocked_tes.return_value = 'mocked_tes.return_value'
        print('foo3.tes() =', foo3.tes())
    print('go out from with')
    print('foo3.tes() =', foo3.tes())
