import leveldb, random
from json import dumps as package, loads as unpackage
DB=leveldb.LevelDB('DB')
def exists_p(key):
    try:
        DB.Get(key)
        return True
    except KeyError:
        return False
def make_salt():
    salt=str(random.getrandbits(24))
    DB.Put('salt', salt)
    try:
        if DB.Get('salt')+'a'==salt+'a': return salt
    except:
        pass
    return make_salt()
if exists_p('salt'):
    salt=DB.Get('salt')
else:
    salt=make_salt()

def get(key, tries=10): 
    key=str(key)
    if tries==0: return 'undefined'
    try:
        return unpackage(DB.Get(salt+key))
    except KeyError:
        return get(key, tries-1)
def put(key, value): 
    key=str(key)
    a=salt+key
    b=package(value)
    return DB.Put(a, b) 
if __name__ == "__main__":
    put('test', 'TEST')
    get('test')
    put('a', True)
    if not get('a')==True: error()
    put('b', False)
    if not get('b')==False: error()
    for i in 'abcdefghijklmnopqrstuvwxyz':
        put(i, i*10)
    for i in range(10000):
        put(str(i), str(i)*1000)
    for i in range(10000):
        if not get(str(i))==str(i)*1000: 
            print('failed test')
            error()
    for i in 'abcdefghijklmnopqrstuvwxyz':
        if not get(i)==i*10: 
            print('failed test')
            error()
    print('passed all tests')
