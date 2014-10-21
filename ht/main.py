import trie, rlp
db=trie.Trie('db', trie.BLANK_ROOT)

def root_hash(): return db.root_hash.encode('hex')
def put(key, value): return db.update(key, rlp.encode(value))
def get(key): return rlp.decode(db.get(key))
def make_proof(key): return db.produce_spv_proof(key)
def verify_proof(root_hash, key, proof): return trie.verify_spv_proof(root_hash, key, proof)
put('abc', '123')
print(get('abc'))
print(root_hash())
