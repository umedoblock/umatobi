# https://docs.python.org/3/library/unittest.mock-examples.html
import datetime
from unittest.mock import patch

import module

manipulated_datetime = datetime.datetime(2011, 11, 11, 11, 11, 11, 111111)

def test_foo(msg=''):
    print(msg)
    foo = module.Foo()
    print('foo =', foo)
    print('foo.method() =', foo.method())
    print('foo.now() =', foo.now())
    print()

if __name__ == "__main__":
    mf = module.Foo()
    print('isinstance(mf, module.Foo) =', isinstance(mf, module.Foo))
    test_foo('= 1 __main__')

#   mocked_Foo_patcher = patch('module.Foo', autospec=True, spec_set=True)
    mocked_Foo_patcher = patch('module.Foo')
    test_foo('= 2 mocked_Foo_patcher = patch(\'module.Foo\')')

    mocked_Foo = mocked_Foo_patcher.start()
    test_foo('= 3 mocked_Foo = mocked_Foo_patcher.start()')

    mocked_foo = mocked_Foo.return_value
    print('type(mocked_foo) =', type(mocked_foo))
    print('type(mf) =', type(mf))
  # print('isinstance(mocked_foo, module.Foo) =', isinstance(mocked_foo, module.Foo))
    test_foo('= 4 mocked_foo = mocked_Foo.return_value')

    mocked_foo.method.return_value = 'the mocked result'
    test_foo('= 5 \'mocked_foo.method.return_value = \'the mocked result\'')

    mocked_foo.now.return_value = manipulated_datetime
    test_foo('= 6 mocked_foo.now.return_value = manipulated_datetime')

    mocked_Foo = mocked_Foo_patcher.stop()
    test_foo('= 7 mocked_Foo_patcher.stop()')
