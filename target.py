import blockchain, custom, tools
def target(DB, length=0):
    """ Returns the target difficulty at a paticular blocklength. """
    db_length=tools.db_get('length')
    if length == 0:
        length = tools.db_get('length')
    if length < 4:
        return '0' * 4 + 'f' * 60  # Use same difficulty for first few blocks.
    trgs=tools.db_get('targets')
    if length <= db_length and str(length) in trgs:
        return trgs[str(length)]  # Memoized, This is a small memory leak. It takes up more space linearly over time. but every time you restart the program, it gets cleaned out.
    def targetTimesFloat(target, number):
        a = int(str(target), 16)
        b = int(a * number)
        return tools.buffer_(str(hex(b))[2: -1], 64)
    def weights(length):
        return [custom.inflection ** (length-i) for i in range(length)]
    def estimate_target(DB):
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
        targets = blockchain.recent_blockthings('targets', DB, custom.history_length)
        w = weights(len(targets))
        tw = sum(w)
        targets = map(blockchain.hexInvert, targets)
        def weighted_multiply(i):
            return targetTimesFloat(targets[i], w[i]/tw)
        weighted_targets = [weighted_multiply(i) for i in range(len(targets))]
        return blockchain.hexInvert(sumTargets(weighted_targets))
    def estimate_time(DB):
        times = blockchain.recent_blockthings('times', DB, custom.history_length)
        blocklengths = [times[i] - times[i - 1] for i in range(1, len(times))]
        w = weights(len(blocklengths))  # Geometric weighting
        tw = sum(w)  # Normalization constant
        return sum([w[i] * blocklengths[i] / tw for i in range(len(blocklengths))])
    retarget = estimate_time(DB) / custom.blocktime(length)
    return targetTimesFloat(estimate_target(DB), retarget)


