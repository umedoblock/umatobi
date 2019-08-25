from unittest.mock import Mock

def __str__(self):
    return 'fooble'

mock = Mock()
mock.__str__ = __str__

print(str(mock))
print(str(1))
