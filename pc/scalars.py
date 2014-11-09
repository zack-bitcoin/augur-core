from cdecimal import Decimal
pi=Decimal('3.141592653589793')
E=Decimal('2.718281828459045')
def dec_greater_than(a, b): return float(a)>float(b)
def factorial(n): return 1 if not dec_greater_than(n, 1) else n*factorial(n-1)
def alternate_sum(v, positive=1, s=0): return s if len(v)==0 else alternate_sum(v[1:], -positive, s+v[0]*positive)
Taylor_series_depth=13
def trig(x, t):
    if not dec_greater_than(x, Decimal('0.0000001')) and dec_greater_than(x, Decimal('-0.0000001')): return 1-t
    if not dec_greater_than(x, -pi): return trig(x+2*pi, t)
    if dec_greater_than(x, pi): return trig(x-2*pi, t)
    a=filter(lambda y: y%2==t, range(Taylor_series_depth))
    a=map(lambda y: (x**y)/factorial(y), a)
    return alternate_sum(a)
def trig_test():
    print(cos(Decimal('0.5')))
    print(sin(Decimal('0.5')))
    import math
    print(math.cos(0.5))
    print(math.sin(0.5))
def cos(x): return trig(x, 0)
def cos_test():
    for i in range(1000):
        print(cos(pi*2*i/1000))
def sin(x): return trig(x, 1)
def mul(a, b): return a*b
def add(a, b): return a+b
def plug_in(x, v):
    c=range(len(v))
    c=map(lambda y: cos(y*pi*x), c)
    c=map(mul, v, c)
    return sum(c)
def integrate(v, m=100): return sum(map(lambda x: plug_in(Decimal(1)*x/100, v), range(m)))
def C(v, B): 
    a=integrate(map(lambda x: E**(x/B), v))
    return B*a.ln()
def cost_to_buy_shares(current_state, shares, B):
    a=C(current_state, B)
    b=C(map(add, current_state, shares), B)
    return b-a

print(cost_to_buy_shares([Decimal('10'),Decimal('50'),0,0,0], [Decimal('10'),0,0,0,0], 1000))
print(cost_to_buy_shares([Decimal('10'),Decimal('50'),0,0,0], [Decimal('5'),0,0,0,0], 1000))
print(cost_to_buy_shares([Decimal('10'),Decimal('50'),0,0,0], [Decimal('5'),Decimal('5'),0,0,0], 1000))
