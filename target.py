import blockchain, custom, tools
from fractions import Fraction
def denominator_limited_sum(l, a=0):
    if len(l)==0: return a
    return denominator_limited_sum(l[1:], (a+l[0]).limit_denominator())
def target(length=0):
    """ Returns the target difficulty at a paticular blocklength. """
    db_length=tools.db_get('length')
    if length == 0: length = db_length
    if length < 4: return '0' * 4 + 'f' * 60  # Use same difficulty for first few blocks.
    trgs=tools.db_get('targets')
    if length <= db_length and str(length) in trgs:
        return trgs[str(length)]  
    def targetTimesFloat(target, number):
        a = int(str(target), 16)
        b = int(a * number)#this should be rational multiplication followed by integer estimation
        return tools.buffer_(str(hex(b))[2: -1], 64)
    def multiply_things(things):
        out=1
        while len(things)>0:
            out=out*things[0].limit_denominator()
            things=things[1:]
        return out
    def rat_power(a, b):#6 seconds per hundred blocks
        things=[]
        while a>1 and b>1:
            if b%2==0:
                a=(a*a).limit_denominator()
                b=b/2
            else:
                things.append(a)
                b=b-1
        if a==0: return 0
        if a==1: return 1
        if b==0: return 1
        if b==1: return multiply_things([a]+things)
    def weights(length):#uses float
        return [rat_power(custom.inflection, (length-i)).limit_denominator() for i in range(length)]
    def estimate_target():
        """
        We are actually interested in the average number of hashes required to
        mine a block. number of hashes required is inversely proportional
        to target. So we average over inverse-targets, and inverse the final
        answer. """
        def sumTargets(l):
            if len(l) < 1:
                return 0
            while len(l) > 1:
                l = [blockchain.hexSum(l[0], l[1])] + l[2:]
            return l[0]
        targets = blockchain.recent_blockthings('targets', custom.history_length)
        w = weights(len(targets))#should be rat instead of float
        tw = denominator_limited_sum(w)
        targets = map(blockchain.hexInvert, targets)
        def weighted_multiply(i):
            return targetTimesFloat(targets[i], w[i]/tw)#this should use rat division instead
        weighted_targets = [weighted_multiply(i) for i in range(len(targets))]
        return blockchain.hexInvert(sumTargets(weighted_targets))
    def estimate_time():
        times = blockchain.recent_blockthings('times', custom.history_length)#should be deterministally turned into rats
        times=map(Fraction, times)
        blocklengths = [times[i] - times[i - 1] for i in range(1, len(times))]
        w = weights(len(blocklengths))  # Geometric weighting
        tw = denominator_limited_sum(w)  # Normalization constant
        return denominator_limited_sum([w[i] * blocklengths[i] / tw for i in range(len(blocklengths))])
    retarget = estimate_time() / custom.blocktime(length)
    return targetTimesFloat(estimate_target(), retarget)


