from cdecimal import Decimal
import python_CustomMath as custommath
def DemocracyRep(x):
    v=[]
    for i in range(len(x)):
        v.append(1)
    return(custommath.ReWeight(v))
def GetRewardWeights(M, Rep=-1, alpha=Decimal('0.1')):
    if Rep==-1:
        Rep=DemocracyRep(M)
    if type(Rep[0])==list:
        Rep=map(lambda x: x[0], Rep)
    Results=custommath.WeightedPrinComp(M, Rep)
    FirstLoading=Results['Loadings']
    FirstScore=Results['Scores']
    a=min(map(abs,FirstScore))
    b=max(FirstScore)
    Set1=map(lambda x: x+a, FirstScore)
    Set2=map(lambda x: x-b, FirstScore)
    Old=custommath.dot([Rep], M)
    New1=custommath.dot([custommath.GetWeight(Set1)], M)
    New2=custommath.dot([custommath.GetWeight(Set2)], M)
    def sub_f(a, b): return a-b
    def f(n): return sum(map(lambda x: x**2, map(sub_f, n[0], Old[0])))
    RefInd=f(New1)-f(New2)
    if(RefInd<=0): AdjPrinComp = Set1  
    else: AdjPrinComp = Set2  
    RowRewardWeighted=Rep
    if max(map(abs,AdjPrinComp))!=0:
        m=custommath.mean(Rep)
        RRW=[]
        for i in range(len(Rep)):
            RRW.append(AdjPrinComp[i]*Rep[i]/m)
        RowRewardWeighted=custommath.GetWeight(RRW)
    SmoothedR=[]
    for i in range(len(Rep)):
        SmoothedR.append(alpha*RowRewardWeighted[i]+(1-alpha)*Rep[i])
    Out = {"FirstL":FirstLoading, "OldRep":Rep, "ThisRep":RowRewardWeighted, "SmoothRep":SmoothedR}  
    return(Out)
def test_GetRewardWeights():
    M = [[1, 1, 0, 0],
         [1, 0, 0, 0],
         [1, 1, 0, 0],
         [1, 1, 1, 0],
         [0, 0, 1, 1],
         [0, 0, 1, 1]]
    '''
{'FirstL': [Decimal('-0.5395366037873049834610773420'),
            Decimal('-0.4570560722424117163006049290'),
            Decimal('0.4570560722424117163006049291'),
            Decimal('0.5395366037873049834610773410')],
 'OldRep': [Decimal('0.1666666666666666666666666667'),
            Decimal('0.1666666666666666666666666667'),
            Decimal('0.1666666666666666666666666667'),
            Decimal('0.1666666666666666666666666667'),
            Decimal('0.1666666666666666666666666667'),
            Decimal('0.1666666666666666666666666667')],
 'SmoothRep': [Decimal('0.1782375696127678871611093569'),
               Decimal('0.1717624303872321128388906431'),
               Decimal('0.1782375696127678871611093569'),
               Decimal('0.1717624303872321128388906431'),
               Decimal('0.1500000000000000000000000000'),
               Decimal('0.1500000000000000000000000000')],
 'ThisRep': [Decimal('0.2823756961276788716110935692'),
             Decimal('0.2176243038723211283889064308'),
             Decimal('0.2823756961276788716110935692'),
             Decimal('0.2176243038723211283889064308'),
             Decimal('0'),
             Decimal('0')]}
    '''
    import pprint
    pprint.pprint(GetRewardWeights(M))
def GetDecisionOutcomes(Mtemp, Rep):
# Determines the Outcomes of Decisions based on the provided reputation (weighted vote)
    #For each column
    out=[]
    for i in range(len(Mtemp[0])):
        Row=[]
        Col=[]
        c=map(lambda x: x[i], Mtemp)
        for j in range(len(c)):
            if type(j) not in [str, unicode]:
                Row.append(Rep[j])
                Col.append(c[j])
        Row=custommath.ReWeight(Row)
        #out.append(custommath.weighted_median(Row, Col))
        print('Row: ' +str(Row))
        print('Col: ' +str(Col))
        out.append(custommath.dot(Col, Row))
    return custommath.switch_row_cols(out)
def test_getdecisionoutcomes():
    M=[[1,    1,    0,    'NA'],
       [1,    0,    0,    0],
       [1,    1,    0,    0],
       [1,    1,    1,    0],
       [0,    0,    1,    1],
       [0,    0,    1,    1]]
    print(GetDecisionOutcomes(M, [1]*6))

test_getdecisionoutcomes()
