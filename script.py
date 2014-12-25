import copy
import tools
def apply_script(f, stack):#this function is a tiny forth-like language.
    do={'swap':(lambda l: [l[1]]+[l[0]]+l[2:]), 
        'drop':(lambda l: l[1:]),
        '*':(lambda l: [l[0]*l[1]]+l[2:]),
        '/':(lambda l: [l[0]/l[1]]+l[2:]),
        '-':(lambda l: [l[0]-l[1]]+l[2:]),
        '+':(lambda l: [l[0]+l[1]]+l[2:])}
    def helper(f, stack): 
        tools.log('stack: ' +str(stack))
        if len(f)==0: return stack
        try:
            f[0]=float(f[0])
            return helper(f[1:], [f[0]]+stack)
        except Exception as exc:
            tools.log(exc)
            return helper(f[1:], do[f[0]](stack))
    return helper(f.split(' '), stack)
def share_value(pm, state):
    #out=dict(map(lambda x: [x, ''], pm['output_state']))
    def helper(stack, algorithm):
        stack_copy=copy.deepcopy(stack)
        stack_copy=apply_script(pm['functions'][algorithm[0]], stack_copy)
        if state in algorithm[1]: 
            s=stack_copy[0]
            if len(algorithm[1])==1:
                return s
            n=2
        else: 
            s=1-stack_copy[0]
            if len(algorithm)==2:
                return s
            n=3
        return s*helper(stack, algorithm[n])
    return helper(pm['results'], pm['algorithm'])
example_pm={'results':[1,0], 'predictions':['obama wins election', 'pinto beans above 80 cents'], 'functions':['swap drop', 'drop'], 'output states':['a', 'b', 'c', 'd'], 'algorithm':[0, ['a', 'b'], [1, ['a']], [1, ['c']]]}
print(share_value(example_pm, 'a'))
print(share_value(example_pm, 'b'))
print(share_value(example_pm, 'c'))
print(share_value(example_pm, 'd'))
example_pm={'results':[0.5], 'predictions':['price of BTC in USD within 200-900'], 'functions':['700 * 200 + 1 / 900 1 / swap - 200 *'], 'output states':['stable-coin', 'vol-coin'], 'algorithm':[0, ['stable-coin']]}
print(share_value(example_pm, 'vol-coin'))
print(share_value(example_pm, 'stable-coin'))
#because the margins are so wide, there has to be a lot more vol-coins than stable coins.
