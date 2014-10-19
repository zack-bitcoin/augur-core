import ht, os, sys
from json import dumps as package, loads as unpackage
def buffer_(str_to_pad, size):
    return str_to_pad.rjust(size, '0')
def last():#this discovers where the end of the list is.
    i=0
    out=0
    while True:
        if ht.file_exists(str(i)):
            j=1
            while True:
                if ht.file_exists(str(i)+'/a'+str(i*1000+j)):
                    out=i*1000+j
                else:
                    #print('file did not exist: db/'+str(i)+'/a'+str(i*1000+j))
                    return out
                j+=1
        else:
            #print('file did not exist: db/'+str(i))
            return out
        i+=1
DB={'last':last()}
#print('DB: ' +str(DB))
def file_part(n): return str(n/1000)
def append(x):
    DB['last']+=1
    f=file_part(DB['last'])
    if not ht.file_exists(f):
        ht.make_file(f)
    ht.raw_write_page(f+'/a'+str(DB['last']), x)
    return DB['last']
def exists(n): 
    f=file_part(n)
    if not ht.file_exists(f): return False
    if not os.path.isfile('db/'+f+'/a'+str(n)): return False
    return True
def lookup(n):
    if not exists(n):
        return {'error':'n is too big'}
    f=file_part(n)
    return ht.raw_read_page(f+'/a'+str(n))
def replace(n, x):
    if not exists(n):
        return {'error':'n is too big'}
    f=file_part(n)
    ht.raw_write_page(f+'/a'+str(n), x)


if __name__ == "__main__":
    for i in range(3000):
        append(str(i)*100)
    print(lookup(999))
    replace(999, 'abc')
    print(lookup(999))
