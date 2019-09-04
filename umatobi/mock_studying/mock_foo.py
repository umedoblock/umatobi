# https://docs.python.org/3/library/unittest.mock-examples.html
from unittest.mock import patch

class Foo:
  def foo(self):
    pass

with patch.object(Foo, 'foo', autospec=True) as mock_foo:
  mock_foo.return_value = 'foo'

  foo = Foo()
  foo.foo()

  mock_foo.assert_called_once_with(foo)
