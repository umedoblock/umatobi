import re, unittest
from unittest import mock
from unittest.mock import MagicMock

class Client(object):
    def _come_to_a_bad_end(self):
        pass

    def wrap(self):
        self._come_to_a_bad_end()

class ClientTests(unittest.TestCase):
    @mock.patch.object(Client, '_come_to_a_bad_end', autospec=True)
    def test_client_start2(self, *mocks):
        client = Client()

        master = MagicMock()

        for mock in reversed(mocks):
            m = re.search('function (.+) at', str(mock))
            func_name = m[1]
          # print('func_name =', func_name)
            master.attach_mock(mock.mock, func_name)

        client.wrap()

        print('list(master.mock_calls) =', list(master.mock_calls))
        print(master.mock_calls[0] == mocks[0])
        print('mocks[0].mock == master.mock_calls[0] is ', mocks[0].mock == master.mock_calls[0])
#       print(dir(master.mock_calls[0]))
#       print(dir(mocks[0]))
        print('------------------------------------------------')
        print('mocks[0] =', mocks[0])
        print('mocks[0].mock =', mocks[0].mock)
#       print('mocks[0].mock.call =', mocks[0].mock.call)
        print('mocks[0].mock_calls =', mocks[0].mock_calls)
        print('type(mocks[0]) =', type(mocks[0]))
        print('------------------------------------------------')
        print('type(master.mock_calls[0]) =', type(master.mock_calls[0]))
        print('master.mock_calls =', master.mock_calls)
        print('master.mock_calls[0] =', master.mock_calls[0])
        print('master.mock_calls[0].mock =', master.mock_calls[0].mock)

        print('------------------------------------------------')
        print('888 mocks[0].mock_calls[0] == master.mock_calls[0] is', mocks[0].mock_calls[0] == master.mock_calls[0])
# ------------------------------------------------
# mocks[0].mock_calls = [call(<__main__.Client object at 0x103248ef0>),
#  call.__eq__(call._come_to_a_bad_end(<__main__.Client object at 0x103248ef0>)),
#  call.__str__()]
# type(mocks[0]) = <class 'function'>
# ------------------------------------------------
# type(master.mock_calls[0]) = <class 'unittest.mock._Call'>
# master.mock_calls = [call._come_to_a_bad_end(<__main__.Client object at 0x103248ef0>),
#  call._come_to_a_bad_end.__eq__(call._come_to_a_bad_end(<__main__.Client object at 0x103248ef0>)),
#  call._come_to_a_bad_end.__str__()]
# master.mock_calls[0] = call._come_to_a_bad_end(<__main__.Client object at 0x103248ef0>)
# master.mock_calls[0].mock = mock

if __name__ == '__main__':
    unittest.main()
