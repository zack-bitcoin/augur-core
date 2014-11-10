# v is used for fourier series. f(x) is used for functions between 0 and 1.
from cdecimal import Decimal
one=Decimal('1')
pi=Decimal('3.141592653589793')
E=Decimal('2.718281828459045')
def dec_greater_than(a, b): return float(a)>float(b)
def factorial(n): return 1 if not dec_greater_than(n, 1) else n*factorial(n-1)
def alternate_sum(v, positive=1, s=0): return s if len(v)==0 else alternate_sum(v[1:], -positive, s+v[0]*positive)
Taylor_series_depth=13
def trig(x, t):
    if not dec_greater_than(x, Decimal('0.0000001')) and dec_greater_than(x, Decimal('-0.0000001')): return 1-t
    if not dec_greater_than(x, -pi): return trig(x+2*pi, t)
    if dec_greater_than(x, 10*pi): return trig(x-11*pi, t)
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
def graph(f, m=100): 
    for i in range(m):
        print(f(Decimal(i)/m))
def cos_test():
    graph(lambda x: cos(pi*2*x))
#cos_test()
def sin(x): return trig(x, 1)
def mul(a, b): return a*b
def add(a, b): return a+b
def plug_in(x, v):
    c=range(len(v))
    c=map(lambda y: cos(y*pi*x), c)
    c=map(mul, v, c)
    return sum(c)
def v2f(v): return lambda x: plug_in(x, v)
def v2f_test():
    print(graph(v2f([1,1,1,1,1])))#should be dirac delta at 0
def integrate(f, m=5): return sum(map(lambda x: f(Decimal(x)/m), range(m)))/m#this m determines initial liaudity=B*ln(m)
def integrate_test():
    def f(x): return x*Decimal('1')
    print(integrate(f))
    print(integrate(f, 1000))
#integrate_test()
def C(v, B): 
    #a=integrate(v2f(map(lambda x: E**(x/B), v)))
    a=integrate(lambda x: E**(v2f(v)(x)/B))
    return B*a.ln()
def cost_to_buy_shares(current_state, shares, B):
    a=C(current_state, B)
    b=C(map(add, current_state, shares), B)
    return b-a
def dirac_delta(a, l): return [Decimal('0.1')]+[a]*(l-1)
def dirac_test():
    a=dirac_delta(Decimal('0.1'), 100)
    print(a)
    R=200
    for i in range(R):
        print(plug_in(Decimal(1)*i/R, a))
#dirac_test()
def DFT(f, s=5):
    def g(f, n): return (lambda x: f(x)*cos(pi*n*x))
    return map(lambda n: integrate(g(f, n), s), range(s))
def DFT_test():
    def c(x):
        if x>one/7 and x<one*2/5: return 100
        return 1
    def d(x):
        n=10**8
        if x<one/20: return 25*n
        if x<one/10: return 4*n
        return 1*n
    def e(x): return one*3/4-x
    def f(x):
        if x>one/2 and x<one/2+one/50: return 50
        if x>one/2-one/20 and x<one/2+one/20: return 10
        return 3
    def g(x):
        if x>0.5: return 100
        return 0
    def h(f):
        v=DFT(f, 90)
        a=v2f(v)
        print(v)
        print('\n\n')
        graph(a)
        print('\n\n')
        #print(integrate(a))
        n=1000
        b=cost_to_buy_shares([0]*len(v), v, n)
        print(b)
        import math
        print(math.e**(float((a(0)-b)/n)))
    h(c)
DFT_test()

#print(cost_to_buy_shares([Decimal('10'),Decimal('50'),0,0,0], [Decimal('10'),0,0,0,0], 1000))
#print(cost_to_buy_shares([Decimal('10'),Decimal('50'),0,0,0], [Decimal('5'),0,0,0,0], 1000))
#print(cost_to_buy_shares([Decimal('10'),Decimal('50'),0,0,0], [Decimal('5'),Decimal('5'),0,0,0], 1000))
