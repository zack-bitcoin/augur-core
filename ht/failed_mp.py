import arr
from json import dumps as package, loads as unpackage
def hash_(x): return hashlib.sha384(x).hexdigest()[0:64]
def det_hash(x): return hash_(package(x, sort_keys=True))
def new_node(s): return ['']*16+[s]
def match_distance(key, node, counter=0):
    if counter>=len(node[0]):
        return counter#get_helper(key, node[1])
    if node[0][counter]==key[0]:
        return match_distance(key[1:], node, counter+1)
    else:
        return counter
def does_it_match(key, node, counter=0):
    if counter>=len(node[0]):
        return True#get_helper(key, node[1])
    if node[0][counter]==key[0]:
        return does_it_match(key[1:],node, counter+1)
    else:
        False
def put(key, value): return put_helper(key.encode('hex'), value, 1)
if not arr.exists(1):
    a=arr.append(new_node(''))
def put_helper(key, value, loc):
    node=arr.lookup(loc)
    if len(node)==2:
        old_key=node[0]
        m=match_distance(key, node)
        if m==len(key):
            node[1]=value
            arr.replace(loc, node)
            return 0
        else:
            N=new_node(key[m+1:])
            N[int(key[m])]=arr.append([key[m+1:], value])
            print('old: ' +str(old_key))
            print('key: ' +str(key))
            print('node: ' +str(node))
            print('m: ' +str(m))
            N[int(old_key[m])]=arr.append([old_key[m+1:], node[1]])
            N=arr.append(N)
            new=[key[:m], N]
            arr.replace(loc, new)
        '''
        if key=='':
            node[1]=value
            arr.replace(loc, node)
            return 0
        else:
            m=match_distance(key, node)
            if does_it_match(key, node):
                return put_helper('', value, node[1])
            else:
                n=arr.append(new_node(value))
                arr.replace(loc, [node[0][0:m], n])
                return 0
        '''
    elif len(node)==17:
        if key=='':
            node[16]=value
            arr.replace(loc, node)
            return 0
        else:
            if node[int(key[0])]=='':
                newloc=arr.append([key[1:], value])
                node[int(key[0])]=newloc
                arr.replace(loc, node)
                return 0#put_helper(key, value, newloc)
            else:
                return put_helper(key[1:], value, node[int(key[0])])
def get(key): return get_helper(key.encode('hex'), 1)
def get_helper(key, loc):
    if loc=='':
        error()
    node=arr.lookup(loc)
    print('key: ' +str(key))
    print('node: ' +str(node))
    if len(node)==2:
        #if key=='':
        #    return node[1]
        m=match_distance(key, node)
        print('m: ' +str(m))
        print('key: ' +str(key))
        print('node: ' +str(node))
        if m==len(key):
            return node[1]
        else:
            return get_helper(key[m:], node[1])
    if len(node)==17:
        if key=='':
            return node[16]
        else:
            return get_helper(key[1:], node[int(key[0])])

put('ap', 55)
put('ab', 56)
put('zz', 56)
put('ap', 57)
#print(get('ab'))
#print(get('ap'))

