# https://docs.python.org/3/library/unittest.mock-examples.html
import datetime
from unittest.mock import patch
from contextlib import contextmanager

import module

# https://www.python.org/dev/peps/pep-0343/
manipulated_datetime = datetime.datetime(2011, 11, 11, 11, 11, 11, 111111)

@contextmanager
def time_machine(time_tunnel):
    # in Nobita's hikidashi.
    with patch('module.Foo') as mocked_Foo:
        test_foo('= 2 with patch(\'module.Foo\') as mocked_Foo:')

        mocked_foo = mocked_Foo.return_value
        print('type(mocked_foo) =', type(mocked_foo))
        test_foo('= 3 mocked_foo = mocked_Foo.return_value')

        mocked_foo.method.return_value = 'the mocked result'
        test_foo('= 4 \'mocked_foo.method.return_value = \'the mocked result\'')

        mocked_foo.now.return_value = time_tunnel
        test_foo('= 5 mocked_foo.now.return_value = manipulated_datetime')

        try:
            yield
        finally:
            pass

def test_foo(msg=''):
    print(msg)
    foo = module.Foo()
    print('foo =', foo)
    print('foo.method() =', foo.method())
    print('foo.now() =', foo.now())
    print()

if __name__ == "__main__":
    test_foo('= 1 __main__')

    time_warp = manipulated_datetime
    with time_machine(time_warp):
        test_foo('= 7 with patch(\'module.Foo\') as mocked_Foo:')

    with patch('module.Foo') as mocked_Foo:
        test_foo('= 2 with patch(\'module.Foo\') as mocked_Foo:')

        mocked_foo = mocked_Foo.return_value
        print('type(mocked_foo) =', type(mocked_foo))
        test_foo('= 3 mocked_foo = mocked_Foo.return_value')

        mocked_foo.method.return_value = 'the mocked result'
        test_foo('= 4 \'mocked_foo.method.return_value = \'the mocked result\'')

        mocked_foo.now.return_value = manipulated_datetime
        test_foo('= 5 mocked_foo.now.return_value = manipulated_datetime')

    test_foo('= 6 without patch(\'module.Foo\') as mocked_Foo:')
