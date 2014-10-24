def make_sfuncs():
    # The imports are here to make sure
    # this only happens inside the main
    # function (which makes it happen ONLY
    # in the process running the main function)
    import sys
    import custom
    import os
    from json import dumps as package, loads as unpackage
    if sys.platform == 'win32': # tentative windows support
        import bsddb
        # hashopen will only make a new database
        # if there isn't already one there.
        DB = bsddb.hashopen(custom.database_name)
        DBget = DB.get
        DBput = lambda k, v: DB.__setitem__(k, v)
    else:
        import leveldb
        # leveldb automatically makes a new database
        # iff there is not one with the same name already.
        # If on already exists, then this just opens it.
        DB = leveldb.LevelDB(custom.database_name)
        DBget = DB.Get
        DBput = DB.Put
    try:
        salt = DBget('salt')
    except KeyError:
        salt = os.urandom(5)
        DBput('salt', salt)
    def sget(key, tries=10):
        if tries==0: return 'undefined'
        try:
            return unpackage(DBget(salt + str(key)))
        except KeyError:
            return sget(key, tries-1)
    def sput(key, value):
        return DBput(salt + str(key), package(value))
    return sget, sput

def main(heart_queue):
    import tools
    import netowrking
    sget, sput = make_sfuncs()
    def default_entry(): return {'count': 0, 'amount': 0, 'votecoin':{}, 'votes':{}, 'shares':{}}
    def get(n, DB={}):
        out=sget(n)
        if out=='undefined':
            return default_entry()
        return out
    def put(key, dic, DB={}): 
        return sput(key, dic)
    def delete(key, DB={}): return put(key, 'undefined', DB)
    def existence(key, DB={}):
        n=str(key)
        out=sget(n)
        return not out=='undefined'
    
    def putCommand(args): return put(args[0], args[1])
    def getCommand(args): return get(args[0])
    def exiCommand(args): return existence(args[0])
    def delCommand(args): return delete(args[0])
    dbfunc={'put':putCommand, 'get':getCommand, 'existence':exiCommand, 'delete':delCommand}
    def responder(command):
        if type(command)!=dict or 'type' not in command:
            tools.log('database main command: ' +str(command))
            tools.log('database main command: ' +str(type(command)))
            return {'error': 'bad data'}
        else:
            return dbfunc[command['type']](command['args'])
    return networking.serve_forever(responder, custom.database_port, heart_queue)
if __name__ == "__main__":
    import Queue
    main(Queue.Queue())
