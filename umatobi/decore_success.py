# Thanks KundaRamaKrishna
# copied from
# https://www.geeksforgeeks.org/decorators-with-parameters-in-python/

def decorator(*args, **kwargs):
    print("Inside decorator")
    def inner(func_sample):
        print("Inside inner function")
        print("I like", kwargs['like'])
        return func_sample
    return inner

@decorator(like="geeksforgeeks")
def func_call():
    print("Inside actual function")

if __name__ == '__main__':
    print('-- 3')
    func_call()
