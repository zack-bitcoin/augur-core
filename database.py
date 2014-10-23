import networking, copy, custom
import leveldb, random
from json import dumps as package, loads as unpackage
import os.path
import tools
salt=0
DB_='DB'
def rand_letters(n): return '' if n==0 else random.choice(alphabet)+rand_letters(n-1)
if not os.path.exists(DB_):
    DB=leveldb.LevelDB(DB_)
    alphabet=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    alphabet+=map(lambda x: x.upper(), alphabet)
    alphabet+=['1','2','3','4','5','6','7','8','9','0']
    salt=rand_letters(5)
    DB.Put('salt', salt)
try:
    DB=leveldb.LevelDB(DB_)
except:
    pass

def sget(key, tries=10): 
    global salt
    if salt==0:
        salt=DB.Get('salt')
    key=str(key)
    if tries==0: return 'undefined'
    try:
        return unpackage(DB.Get(salt+key))
    except KeyError:
        return sget(key, tries-1)
def sput(key, value): 
    global salt
    if salt==0:
        salt=DB.Get('salt')
    key=str(key)
    a=salt+key
    b=package(value)
    return DB.Put(a, b) 

def main(heart_queue):
    def responder(command):
        if type(command)!=dict or 'type' not in command:
            tools.log('database main command: ' +str(command))
            tools.log('database main command: ' +str(type(command)))
            return {'error': 'bad data'}
        else:
            return dbfunc[command['type']](command['args'])
    return networking.serve_forever(responder, custom.database_port, heart_queue)
default_entry={'count': 0, 'amount': 0, 'votecoin':{}, 'votes':{}, 'shares':{}}
def get(n, DB={}):
    out=sget(n)
    if out=='undefined':
        return copy.deepcopy(default_entry)
    return out
def put(key, dic, DB={}): 
    return sput(key, dic)
def delete(key, DB={}): return db_put(key, 'undefined', DB)
def existence(key, DB={}):
    n=str(key)
    out=sget(n)
    return not out=='undefined'

def putCommand(args): return put(args[0], args[1])
def getCommand(args): return get(args[0])
def exiCommand(args): return existence(args[0])
def delCommand(args): return delete(args[0])
dbfunc={'put':putCommand, 'get':getCommand, 'existence':exiCommand, 'delete':delCommand}
if __name__ == "__main__":
    import Queue
    main(Queue.Queue())
