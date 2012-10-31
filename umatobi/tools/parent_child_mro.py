# mro means Method Resolution Order.

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
