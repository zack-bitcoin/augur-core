"""a python version of the R program at https://github.com/psztorc/Truthcoin
"""
#import python_ConsensusMechanism as consensus
import tools, pc
#import python_CustomMath as custommath

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
def GetWeight(Vec, AddMean=0):
    """Takes an array (vector in practice), and returns proportional
    distance from zero."""
    New = abs(Vec)       #Absolute Value
    if AddMean == 1:     #Add the mean to each element of the vector
        New = New + mean(New)
    if sum(New) == 0:    #Catch an error here
        New = New + 1
    New = New/sum(New)   #Normalize
    return(New)

def main(m, weights):
    a=pc.Factory(m, weights)
    return {'outcome':a['Decisions']['DecisionOutcome_Final'],
            'author_bonus':a['Decisions']['Author Bonus'],
            'participation':a['Participation'],
            'certainty':a['Decisions']['Certainty'],
            'votecoin_bonus_for_voters':a['Agents']['SmoothRep'],
            'truthcoin_bonus_for_voters':a['Agents']['RowBonus']}
if __name__ == "__main__":
    m=[[1, 1, 1, 1, 1], ['NA', 'NA', 'NA', 'NA', 'NA'], ['NA', 'NA', 'NA', 'NA', 'NA']]
    m=[[1, 1, 1, 1, 0], [0, 0, 0, 0, 1], [0, 0, 0, 0, 0]]
    m=[[1, 1, 0, 'NA'], 
       [1, 0, 0, 0], 
       [1, 1, 0, 0],
       [1, 1, 1, 0],
       [0, 0, 1, 1],
       [0, 0, 1, 1]]
    #w=[[1294], [1], [1294]]
    w=[[1],[1],[1],[1],[1],[1]]
    #w=[[1],[2],[3],[4]]
    #m=[[0,0,0],[0,1,0],[0,0,1]]
    #print(dem_main(m))
    print(main(m, w))

