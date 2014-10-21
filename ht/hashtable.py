#!/usr/bin/env python
import ht, arr
def put(key, value): return ht.put(key, arr.append(value))
def get(key): 
    a=ht.get(key)
    if a=='undefined': return a
    return arr.lookup(a)
if __name__ == "__main__":
    '''
    print('testing hashtable')
    passed=True
    for i in range(5000):
        put(str(i), i)
        get(str(i))
        if i%50==0:
            print(i)
    for i in range(5000):
        if get(str(i))!=i:
            passed=False
            print('error on key '+str(i))
    '''
    for i in 'abcdefghijklmnopqrstuvwxyz':
        put(i, i*10)
    for i in range(10000):
        put(str(i), str(i)*5)
    for i in range(10000):
        if not get(str(i))==str(i)*5: error()
    for i in 'abcdefghijklmnopqrstuvwxyz':
        if not get(i)==i*10: error()


