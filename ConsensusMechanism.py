"""a python version of the R program at https://github.com/psztorc/Truthcoin
"""
import consensus, numpy, custommath

def keep_nums(t):
    if type(t)==list:
        out=[]
        for i in t:
            out.append(keep_nums(i))
        return out
    if type(t)==int:
        return False
    else:
        return True

def main(m, weights):
    weights=numpy.array(weights)
    weights=custommath.GetWeight(weights)
    a=numpy.array(m)
    k=keep_nums(m)
    a=numpy.ma.masked_array(a, mask=k)
    #a=numpy.ma.masked_array(a, numpy.isnan(a))
    a=consensus.Factory(a, Rep=weights)
    return {'outcome':a['Decisions']['DecisionOutcome_Final'],
            'author_bonus':a['Decisions']['Author Bonus'],
            'participation':a['Participation'],
            'certainty':a['Decisions']['Certainty'],
            'votecoin_bonus_for_voters':a['Agents']['SmoothRep'],
            'truthcoin_bonus_for_voters':a['Agents']['RowBonus']}

if __name__ == "__main__":
    m=[[1, 1, 1, 1, 1], ['NA', 'NA', 'NA', 'NA', 'NA'], ['NA', 'NA', 'NA', 'NA', 'NA']]
    #m=[[1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
    w=[[1294], [1], [1294]]
    #w=[[1],[2],[3],[4]]
    #m=[[0,0,0],[0,1,0],[0,0,1]]
    #print(dem_main(m))
    print(main(m, w))

