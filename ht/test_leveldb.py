import leveldb
DB=leveldb.LevelDB('da')
def get_data(key): return DB.Get(key)
def put_data(key, value): return DB.Put(key, value)

if __name__ == "__main__":
    #easy example
    s='this is a string that will be stored in the database, and then recalled'
    put_data('test', s)
    if not get_data('test')==s: error()
    #del_data(a)#delete the string from the database
    #if not get_data(a)=='undefined': error()

    #Speed test
    import time
    t0=time.time()
    for i in range(100000):
        put_data(str(i), '\x01'*60)
    t1=time.time()
    print('added 10 mb to database in '+str(t1-t0)+ ' seconds.')
    
    #stored values are what you expect test.
    for i in range(1000):
        n=str(i)*1000
        put_data(str(i), n)
    for i in range(1000):
        n=str(i)*1000
        if not get_data(str(i))==n: error()
    print('passed all tests')
