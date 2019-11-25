# umatobi simulator
#
# Copyright (c) 2012-2019 梅濁酒(=umedoblock)
#
# This software is released under the MIT License.
# https://github.com/umedoblock/umatobi

# mro means Method Resolution Order.
# see Objects/typeobject.c
'''
Method resolution order algorithm C3 described in
"A Monotonic Superclass Linearization for Dylan",
by Kim Barrett, Bob Cassel, Paul Haahr,
David A. Moon, Keith Playford, and P. Tucker Withington.
(OOPSLA 1996)
'''

class Parent(object):
    def __init__(self):
        print('Parent.__init__()')
        self.update_key()
    def update_key(self):
        print('Parent.update_key()')

class Child(Parent):
    def __init__(self):
        print('Child.__init__()')
        super().__init__()
    def update_key(self):
        print('Child.update_key()')
        super().update_key()

child = Child()
print()
child.update_key()

'''
予想
Child.__init__()
Parent.__init__()
Child.update_key()
Parent.update_key()

Child.update_key()
Parent.update_key()

結果
:!p3 /home/umetaro/repos/svn/work/py/parent_child.py
Child.__init__()
Parent.__init__()
Child.update_key()
Parent.update_key()

Child.update_key()
Parent.update_key()
'''
