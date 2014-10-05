#!/usr/bin/env python
import ht, arr
import time
def put(key, value): return ht.put(key, arr.append(value))
def get(key): 
    a=ht.get(key)
    if a=='n': return 'undefined'
    return arr.lookup(a)

def test_1():
    i=0
    while True:
        put('test', i)
        time.sleep(1)
        i+=1

def test_2():
    while True:
        time.sleep(0.1)
        print(get('test'))
def test_3():
    while True:
        print(get('test'))

if __name__ == "__main__":
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


