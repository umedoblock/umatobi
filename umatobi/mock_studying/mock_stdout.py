# https://docs.python.org/3/library/unittest.mock.html?highlight=mock
from io import StringIO

from unittest.mock import patch

def foo():
    print('Something')

@patch('sys.stdout', new_callable=StringIO)
def test(mock_stdout):
    foo()
    assert mock_stdout.getvalue() == 'Something1\n'

test()
