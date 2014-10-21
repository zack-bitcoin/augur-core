db=open('DB', 'w+r')
def address2int(address): return int(address.encode('hex'), 16)
def buffer(a, l=4, b='\x00'):
    if len(a)==l: return a
    return buffer(b+a, l, b)
def int2address(n):
    s = '%x' % n
    if len(s) & 1:
        s = '0' + s
    return buffer(s.decode('hex'))
def get_block(n):
    db.seek(n*64)
    return db.read(64)
def put_block(n, block):
    if len(block)>64: error()
    db.seek(n*64)
    return db.write(block)
def del_block(n):
    db.seek(n*64+60)
    db.write('\x00'*4)
def reserve_block(n):
    db.seek(n*64+60)
    db.write('\xff'*4)
def reserved_p(n):
    db.seek(n*64+60)
    t=db.read(4)
    if t=='': return False
    return address2int(t)!=0
def address_null_p(n):
    db.seek(n*64+60)
    t=db.read(4)
    if t=='': return False
    return t=='\xff\xff\xff\xff'
first_empty=[0]
def first_empty_block(first_empty=first_empty):
    if reserved_p(first_empty[0]):
        first_empty=[-1]
        while True:
            first_empty[0]+=1
            if not reserved_p(first_empty[0]):
                return first_empty[0]
    else:
        return first_empty[0]
def put_data(data, b=0):
    if b==0:
        b=first_empty_block()
    if len(data)>60:
        reserve_block(b)
        b2=first_empty_block()
        block=data[:60]+int2address(b2)
        put_block(b, block)
        return put_data(data[60:], b2)
    else:
        block=buffer(data, 60, '\x00')+'xff'*4
        put_block(b, block)
def get_data(n):
    b=get_block(n)
    if
put_data('abcd'*100)


'''
reserved_p(0)
print(first_empty_block())
put_block(0, 'a'*64)
put_block(1, 'a'*64)
print(reserved_p(0))
#del_block(0)
print(reserved_p(0))
print(first_empty_block())
'''
