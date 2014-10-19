import arr, hashlib
from json import dumps as package, loads as unpackage
empty=''
def hash_(x): return hashlib.sha384(x).hexdigest()[0:64]
def det_hash(x): return hash_(package(x, sort_keys=True))
def hex_to_int(h): return (lambda a: a-87 if a>90 else a-48)(ord(str(h)))
def key_to_path(key): return map(hex_to_int, key)
def arr_edit(loc, f):
    n=lookup(loc)
    n=f(n)
    arr.replace(loc, n)
if not arr.exists(1):
    arr.append([empty]*17)
def overlap(a, b, c=[]): 
    def h(a, b): return a==[] or b==[] or a[0]!=b[0]
    return (a, b, c) if h(a, b) else overlap(a[1:], b[1:], c+[a[0]])
def get(key): return get_h(key_to_path(key), 1)
def get_h(p, loc):
    node=lookup(loc)
    if len(node)==17:
        if p==[]:
            return node[16]
        return get_h(p[1:], node[p[0]])
    if len(node)==2:
        if p==node[0]:
            return node[1]
        else:
            return get_h(p[len(node[0]):], node[1])
def alloc(node): return ['a', arr.append(node)]
def lookup(loc): 
    if type(loc)==int: return arr.lookup(loc)
    return lookup(loc[1])
def replace(loc, node):
    if type(loc)==int: return arr.replace(loc, node)
    return replace(loc[1], node)    
def put(key, value): return put_h(key_to_path(key), value, 1)
def put_h(p, value, loc):
    node=lookup(loc)
    if len(node)==17:
        if p==[]:
            node[16]=value
            replace(loc, node)
            return
        if node[p[0]]==empty:
            n=alloc([p[1:], value])
            node[p[0]]=n
            replace(loc, node)
            return
        return put_h(p[1:], value, node[p[0]])
    if len(node)==2:
        n, b, common=overlap(node[0], p)
        if common==[]:
            new_node=make_branch(n, node[1], b, value)
            replace(loc, new_node)
            return
        if len(common)==1:
            br=make_branch(n, node[1], b, value)
            new_node=[empty]*17
            new_node[common[0]]=alloc(br)
            replace(loc, new_node)
            return
        br=make_branch(n, node[1], b, value)
        new_node=[common, alloc(br)]
        replace(loc, new_node)
        return
def make_branch(key1, value1, key2, value2):
    b=[empty]*17
    if key1==[]: b[16]=value1
    else: b[key1[0]]=alloc([key1[1:], value1]) 
    if key2==[]: b[16]=value2
    else: b[key2[0]]=alloc([key2[1:], value2])
    return b
def address_p(n): return type(n)==list and len(n)==2 and n[0]=='a'
def hash_root():
    node_hashes={}
    def hash_node(n):
        if n in node_hashes: return node_hashes(n)
        node=lookup(n)
        v=map(lambda x: hash_node(x[1]) if address_p(x) else x, node)
        v2=map(lambda x: x[1] if address_p(x) else x, node)
        out=det_hash(v)
        print('node : ' +str(v2))
        print('node hash ' + str(n) + ' ' +str(out))
        node_hashes[n]=out
        return out
    out=hash_node(1)
    #print('node hashes: ' +str(node_hashes))
    return out


if __name__ == "__main__":
    for i in range(0,5):
        put(str(i), str(i)*5)
    for i in range(1000,1005):
        put(str(i), str(i)*5)
    if False:
        for i in range(25):
            print(get(str(i)))
        for i in range(100,125):
            print(get(str(i)))
    '''
    put('345', 'apple')
    put('5b', 'pear')
    put('14', 'apple')
    print(get('123'))
    print(get('14'))
    print(get('345'))
    create_branch( 1, '100', 'zack')
    create_branch( 2, '0', 'hess')
    #put('100', 'zack')
    #put('1', 'hess')
    #print(get('1'))
    print(get('100'))
    '''
    print(hash_root())
    #print(get('abc'))
