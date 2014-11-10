def simpson(f, a, b, n):
    h=(b-a)/n
    k=0.0
    x=a + h
    for i in range(1,n/2 + 1):
        k += 4*f(x)
        x += 2*h

    x = a + 2*h
    for i in range(1,n/2):
        k += 2*f(x)
        x += 2*h
    return (h/3)*(f(a)+f(b)+k)

def f(x): return 1
print(simpson(f, 0, 1, 100))
