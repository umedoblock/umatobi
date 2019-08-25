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
        test_foo('= 2 ride on the time machine.')

        mocked_foo = mocked_Foo.return_value
        test_foo('= 3 switch on the time machine.')

        mocked_foo.method.return_value = 'the mocked result'
        test_foo('= 4 works it !')

        mocked_foo.now.return_value = time_tunnel
        test_foo('= 5 set time travel era.')

        try:
            print('= 6 go to the era.')
            print()
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
    test_foo('= 1 Nobita and Doraemon come on __main__')

    time_warp = manipulated_datetime
    with time_machine(time_warp):
        test_foo(f'= 7 arrive at the era, time_machine(time_warp={time_warp}):')

    test_foo('= 8 ride off the time_machine')
