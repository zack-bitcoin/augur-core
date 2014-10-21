import arr, hashlib
from json import dumps as package, loads as unpackage
empty=''
def hash_(x): return hashlib.sha384(x).hexdigest()[0:64]
def det_hash(x): return hash_(package(x, sort_keys=True))
def hex_to_int(h): return (lambda a: a-87 if a>90 else a-48)(ord(str(h)))
def key_to_path(key): return map(hex_to_int, key)
def alloc(node): return ['a', arr.append(node)]
def lookup(loc): 
    if type(loc)==int: return arr.lookup(loc)
    return lookup(loc[1])
def replace(loc, node):
    if type(loc)==int: return arr.replace(loc, node)
    return replace(loc[1], node)    
def arr_edit(loc, f):
    n=lookup(loc)
    n=f(n)
    arr.replace(loc, n)
if not arr.exists(1):
    alloc([empty]*17)
def overlap(a, b, c=[]): 
    def h(a, b): return a==[] or b==[] or a[0]!=b[0]
    return (a, b, c) if h(a, b) else overlap(a[1:], b[1:], c+[a[0]])
def get(key): return get_h(key_to_path(det_hash(key)), 1)
def get_h(p, loc):
    node=lookup(loc)
    if p==[]:
        return node[16]
    return get_h(p[1:], node[p[0]][1])
def make_branch(key1, value1, key2, value2):
    b=[empty]*17
    if key1==key2: return [key1, value2]
    if key1==[]: b[16]=value1
    else: b[key1[0]]=alloc([key1[1:], value1]) 
    if key2==[]: b[16]=value2
    else: b[key2[0]]=alloc([key2[1:], value2])
    return b
def put(key, value): return put_h(key_to_path(det_hash(key)), value, 1)
def put_h(p, value, loc):
    node=lookup(loc)
    if p==[]:
        node[16]=value
        replace(loc, node)
        return
    if node[p[0]]==empty:
        n=alloc([empty]*17)
        node[p[0]]=n
        replace(loc, node)
    return put_h(p[1:], value, node[p[0]])
def address_p(n): return type(n)==list and len(n)==2 and n[0]=='a'
def hash_root():
    node_hashes={}
    def hash_node(n):
        if n in node_hashes: return node_hashes(n)
        node=lookup(n)
        v=map(lambda x: hash_node(x[1]) if address_p(x) else x, node)
        v2=map(lambda x: x[1] if address_p(x) else x, node)
        out=det_hash(v)
        node_hashes[n]=out
        return out
    out=hash_node(1)
    return {'root': out, 'nodes':node_hashes}
def make_proof(key, node_hashes=0): 
    if node_hashes==0:
        node_hashes=hash_root()['nodes']
    return make_proof_h(key_to_path(key), 1, node_hashes)
def make_proof_h(p, loc, node_hashes):
    node=lookup(loc)
    if p==[]:
        return []
    a=[map(lambda x: node_hashes[x[1]] if address_p(x) else x, node)]
    print('p: ' +str(p))
    print('node: ' +str(node))
    return a+make_proof_h(p[1:], node[p[0]][1], node_hashes)
def check_proof(proof, root):
    if len(proof)==1: return root==det_hash(proof[0])
    else: return det_hash(proof[-1]) in proof[-2] and check_proof(proof[:-1], root)
    
if __name__ == "__main__":
    for i in range(0,100):
        put(str(i), str(i)*5)
    for i in range(1000,1100):
        put(str(i), str(i)*5)
    for i in range(0,100):
        if not get(str(i))==str(i)*5: error()
    for i in range(1000,1100):
        if not get(str(i))==str(i)*5: error()
    r=hash_root()
    p=make_proof('10', r['nodes'])
    print(check_proof(p, r['root']))

