db=open('DB', 'w+r')
data_size=60
address_size=4
block_size=data_size+address_size
def address2int(address): 
    if address=='': return 0
    return int(address.encode('hex'), 16)
def address(n):
    db.seek(n*block_size+data_size)
    a=db.read(address_size)
    return address2int(a)
def unbuffer(a, b='\x00'):
    if a[0]==b: return unbuffer(a[1:], b)
    else: return a
def buffer(a, l=address_size, b='\x00'):
    if len(a)==l: return a
    return buffer(b+a, l, b)
def int2address(n):
    s = '%x' % n
    if len(s) & 1:
        s = '0' + s
    return buffer(s.decode('hex'))
def get_block(n):
    db.seek(n*block_size)
    a=db.read(block_size)
    if a[data_size:]=='\x00'*address_size: return 'undefined'
    return a
def put_block(n, block):
    if len(block)>block_size: error()
    db.seek(n*block_size)
    return db.write(block)
put_block(0, '\xff'*block_size)
def empty_p(n):
    db.seek(n*block_size+data_size)
    a=db.read(address_size)
    return a=='\x00'*address_size
def del_block(n):
    db.seek(n*block_size+data_size)
    db.write('\x00'*address_size)
def reserve_block(n):
    db.seek(n*block_size+data_size)
    db.write('\xff'*address_size)
def reserved_p(n):
    db.seek(n*block_size+data_size)
    t=db.read(address_size)
    if t=='undefined': return False
    return address2int(t)!=0
def address_null_p(n):
    db.seek(n*block_size+data_size)
    t=db.read(address_size)
    if t=='undefined': return False
    return t=='\xff\xff\xff\xff'
first_empty=0
def first_empty_block():
    global first_empty
    if reserved_p(first_empty):
        while True:
            if not reserved_p(first_empty):
                return first_empty
            first_empty+=1
    else:
        return first_empty
def put_data(data, b=0, final_out=0):
    data=unbuffer(data)
    if b==0:
        b=first_empty_block()
        final_out=b
    if len(data)>data_size:
        reserve_block(b)
        b2=first_empty_block()
        block=data[:data_size]+int2address(b2)
        put_block(b, block)
        return put_data(data[data_size:], b2, final_out)
    else:
        block=buffer(data, data_size, '\x00')+'\xff\xff\xff\xff'
        put_block(b, block)
        return final_out
def get_data(n): return unbuffer(get_data_helper(n))
def get_data_helper(n):
    if n==0: return 'undefined'
    b=get_block(n)
    if b=='undefined': return b
    if empty_p(n):
        return 'undefined'
    if address_null_p(n):
        return b[:data_size]
    else:
        return b[:data_size]+get_data(address(n))
def del_data(n, first_empty=first_empty):
    if address_null_p(n):
        del_block(n)
        first_empty=min(n, first_empty)
    else:
        del_data(address(n))
        del_block(n)
        first_empty=min(n, first_empty)
def test_1():
    import time
    t0=time.time()
    for i in range(1000):
        put_data('\x01'*1000)
    t1=time.time()
    print('added 10 mb to database in '+str(t1-t0)+ ' seconds.')

if __name__ == "__main__":
    #easy example
    s='this is a string that will be stored in the database, and then recalled'
    a=put_data(s)
    if not get_data(a)==s: error()
    del_data(a)#delete the string from the database
    if not get_data(a)=='undefined': error()

    #Speed test
    import time
    t0=time.time()
    for i in range(100000):
        put_data('\x01'*data_size)
    t1=time.time()
    print('added 10 mb to database in '+str(t1-t0)+ ' seconds.')
    
    #stored values are what you expect test.
    l=[]
    for i in range(1000):
        n=str(i)*1000
        l.append([put_data(n), n])
    for i in l:
        if not get_data(i[0])==i[1]: error()
    print('passed all tests')
