import arr, hashlib
from json import dumps as package, loads as unpackage
#pair: [key_part, address/value]
#branch: [address, address, ... , address, value]#location of address encodes a nibble of the key.
if not arr.exists(1):
    arr.append(['',''])
def hex_to_int(h): return (lambda a: a-87 if a>90 else a-48)(ord(str(h)))
def key_to_path(key): return map(hex_to_int, key.encode('hex'))
def no_overlap_p(a, b): return a=='' or b=='' or a[0]!=b[0]
def overlap(a, b, c=''): return (a, b, c) if no_overlap_p(a, b) else overlap(a[1:], b[1:], c+a[0])
def arr_edit(loc, f):
    n=arr.lookup(loc)
    n=f(n)
    arr.replace(loc, n)
def create_pair(loc, key, value): return arr_edit(loc, lambda n: create_pair_helper(n, key, value))
def create_pair_helper(branch, key, value): 
    if key=='':  branch[16]=value
    else: branch[hex_to_int(key[0])]=['a', arr.append([key[1:], value])]
    return branch
def create_branch(loc, key, value): return arr_edit(loc, lambda n: create_branch_helper(n, key, value))
def create_branch_from_branch(loc, key, value): return arr_edit(loc, lambda n: create_branch_from_branch_helper(n, key, value))
def create_branch_helper(pair, key, value):
    b=['']*17
    old_key, new_key, common=overlap(pair[0], key)
    create_pair_helper(b, old_key, pair[1])
    create_pair_helper(b, new_key, value)
    if len(common)>0:
        b=arr.append(b)
        return [common, ['a', b]]
    else:
        return b
        #create_pair_helper(b, old_key[1:],
def create_branch_from_branch_helper(b_old, key, value):
    b_new=['']*16+[value]
    b_new=arr.append(b_new)
    b_old[hex_to_int(key[0])]=['a', b_new]
    return b_old

    old_key, new_key, common=overlap(pair[0], key)
    create_pair_helper(b, old_key, pair[1])
    create_pair_helper(b, new_key, value)
    b=arr.append(b)
    return [common, ['a', b]]
def address_p(n): return type(n)==list and len(n)==2 and n[0]=='a'
def put(key, value, loc=1):
    node=arr.lookup(int(loc))
    if len(node)==17: #looking at a branch
        if key=='': 
            node[16]=value
            arr.replace(loc, node)
            return 
        n=node[hex_to_int(key[0])]
        if address_p(n):
            return put(key[1:], value, n[1])
        if n=='':
            if len(key)>1:
                print('create_pair( ' +str(loc)+' '+str(key)+' '+str(value))
                return create_pair(loc, key, value)
            else:
                print('create_branch( ' +str(loc)+' '+str(key)+' '+str(value))
                return create_branch_from_branch(loc, key, value)
                
    elif len(node)==2: #looking at a pair
        old_key, new_key, common=overlap(node[0], key)
        if key==node[0]:
            if address_p(node[1]):
                return put('', value, node[1][1])
            else:
                node[1]=value
                arr.replace(loc, node)
                return
        if address_p(node[1]):
            return put(key[len(node[0]):], value, node[1][1])
        print('create_branch( ' +str(loc)+' '+str(key)+' '+str(value))
        return create_branch(loc, key, value)
def get(key, loc=1):
    node=arr.lookup(int(loc))
    if len(node)==17: 
        if key=='': return node[16]
        return get(key[1:], node[hex_to_int(key[0])][1])
    elif len(node)==2: 
        if key==node[0]: 
            if address_p(node[1]):
                return get('', node[1][1])
            else:
                return node[1]
        return get(key[len(node[0]):], node[1][1])
def hash_(x): return hashlib.sha384(x).hexdigest()[0:64]
def det_hash(x): return hash_(package(x, sort_keys=True))
def hash_root():
    node_hashes={}
    def hash_node(n):
        if n in node_hashes: return node_hashes(n)
        node=arr.lookup(n)
        v=map(lambda x: hash_node(x[1]) if address_p(x) else x, node)
        v2=map(lambda x: x[1] if address_p(x) else x, node)
        out=det_hash(v)
        print('node : ' +str(v2))
        print('node hash ' + str(n) + ' ' +str(out))
        node_hashes[n]=out
        return out
    out=hash_node(1)
    print('node hashes: ' +str(node_hashes))
    return out
if __name__ == "__main__":
    for i in range(0,5):
        put(str(i), str(i)*5)
    for i in range(100,105):
        put(str(i), str(i)*5)
    for i in range(5):
        print(get(str(i)))
    for i in range(100,105):
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
