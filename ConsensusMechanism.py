"""a python version of the R program at https://github.com/psztorc/Truthcoin
"""
import consensus, numpy, custommath
def main(m, weights):
    weights=numpy.array(weights)
    weights=custommath.GetWeight(weights)
    a=numpy.array(m)
    a=numpy.ma.masked_array(a, numpy.isnan(a))
    a=consensus.Factory(a, Rep=weights)
    return {'outcome':a['Decisions']['DecisionOutcome_Final'],
            'author_bonus':a['Decisions']['Author Bonus'],
            'participation':a['Participation'],
            'certainty':a['Decisions']['Certainty'],
            'votecoin_bonus_for_voters':a['Agents']['SmoothRep'],
            'truthcoin_bonus_for_voters':a['Agents']['RowBonus']}
if __name__ == "__main__":
    m=[[0,0,0],[0,1,0],[0,0,1],[0,0,0]]
    print(dem_main(m))
    print('now with weightings')
    print(main(m, [[1],[2],[3],[4]]))

