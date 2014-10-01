import random, hashlib, os
from json import dumps as package, loads as unpackage
page_size=100
default_db='db_0'
def write_page(file, txt): 
    with open('db/'+file, 'w') as myfile: myfile.write(package(txt))
def read_page(file):
    with open('db/'+file, 'r') as myfile: return unpackage(myfile.read())
def key_hash(key): return int(hashlib.md5(key).hexdigest()[0:5], 16)%page_size
def allocate_page(file): write_page(file,  ['n']*page_size)
def get(key, file=default_db):
    a=get_raw(key, file)
    return get(key, a['page']) if 'page' in a else a['value']
def get_raw(key, file):
    a=read_page(file)[key_hash(key+file)]
    return {'value':'undefined'} if a=='n' else a
def put(key, value, file=default_db, depth=0):
    a=read_page(file)
    h=key_hash(key+file)
    old=get_raw(key, file)
    if ('value' in old and old['value']=='undefined') or ('key' in old and old['key']==key):
        a[h]={'value':value, 'key':key}
        write_page(file, a)
    elif 'page' in old:
        return put(key, value, old['page'], depth+1)
    else: #need to create new page recursively
        f='db_'+str(random.getrandbits(40))
        allocate_page(f)
        a[h]={'page':f}
        write_page(file, a)
        put(key, value, f)
        put(old['key'], old['value'], f)
try: os.mkdir('db')
except: pass
try: 
    with open('db/'+default_db, 'r') as file: pass
except: allocate_page(default_db)


if __name__ == "__main__":
    for i in range(1000):
        put(str(i), str(i))
        print(i)
    for i in range(10):
        print(get(str(i*10)))

