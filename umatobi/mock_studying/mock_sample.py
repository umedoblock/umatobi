# https://docs.python.org/3/library/unittest.mock-examples.html
from unittest.mock import patch

import module

def some_function():
    instance = module.Foo()
    return instance.method()

if __name__ == "__main__":
    result = some_function()
    print('first try')
    print('result =', result)
    print()

    with patch('module.Foo') as mock:
        instance = mock.return_value
        instance.method.return_value = 'the result'

        result = some_function()
        print('second try')
        print('result =', result)
        assert result == 'the result'
