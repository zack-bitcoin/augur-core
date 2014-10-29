import python_CustomMath
dot=python_CustomMath.dot

def DemocracyRep(X):
    v=[]
    for i in range(len(x)):
        v.append(1)
    Rep=custommath.ReWeight(v)
def GetRewardWeights(M, Rep=-1, alpha=0.1):
    if Rep==-1:
        Rep=DemocracyRep(M)
    if type(Rep[0])==list:
        Rep=map(lambda x: x[0], Rep)
    Results=python_CustomMath.WeightedPrinComp(M, Rep)
    FirstLoading=Results['Loadings']
    FirstScore=Results['Scores']
    Set1=FirstScore+min(map(abs,FirstScore))
    Set2=FirstScore-max(FirstScore)
    Old=python_CustomMath.dot(Rep, M)
    #Old=dot(Rep,M)
    New1=python_CustomMath.GetWeight(python_customMath.dot(Set1, M))
    New2=python_CustomMath.GetWeight(python_customMath.dot(Set2, M))
    RefInd = sum( (New1-Old)**2) -  sum( (New2-Old)**2)
    if(RefInd<=0): AdjPrinComp = Set1  
    else: AdjPrinComp = Set2  
    RowRewardWeighted=Rep
    if max(map(abs,AdjPrinComp))!=0:
        m=python_CustomMath.mean(Rep)
        RRW=[]
        for i in range(len(Rep)):
            RRW.append(AdjPrinComp[i]*Rep[i]/m)
        RowRewardWeighted=python_CustomMath.GetWeight(RRW)
    SmoothedR=[]
    for i in range(len(Rep)):
        SmoothedR.append(alpha*RowRewardWeighted[i]+(1-alpha)*Rep[i])
    Out = {"FirstL":FirstLoading, "OldRep":Rep, "ThisRep":RowRewardWeighted, "SmoothRep":SmoothedR}  
    return(Out)
#def GetDecisionOutcomes(Mtemp, Rep, ScaleIndex):
# Determines the Outcomes of Decisions based on the provided reputation (weighted vote)





def GetRewardWeights(M, Rep=-1, Alpha=0.1):
    if Rep==-1:
        print('Rep: ' +str(Rep))
        Rep=DemocracyCoin(M)
    Results = python_CustomMath.WeightedPrinComp(M,Rep)
    print('Results: '+str(Results))
    Rep = GetWeight(Rep)
    FirstLoading = Results['Loadings'] #The first loading is designed to indicate which Decisions were more 'agreed-upon' than others. 
    FirstScore   = Results['Scores'] #The scores show loadings on consensus (to what extent does this observation represent consensus?)
    a=abs(min(FirstScore))
    b=max(FirstScore)
    Set1=map(lambda x: x+a, FirstScore)
    Set2=map(lambda x: x-b, FirstScore)
    Old=dot(Rep, M)
    New1=dot(GetWeight(Set1), M)
    New2=dot(GetWeight(Set2), M)
    a=0
    b=0
    for i in range(len(Old)):
        a+=(New1[i]-Old[i])**2
        b+=(New2[i]-Old[i])**2
    RefInd=a-b
    if RefInd<=0: AdjPrinComp=Set1
    if RefInd>0: AdjPrinComp=Set2
    RowRewardWeighted=Rep
    print(AdjPrinComp)
    if(max(map(abs, AdjPrinComp)))!=0: 
        v=[]
        m=mean(Rep)
        for i in range(len(Rep)):
            v.append(AdjPrinComp[i]*Rep[i]/m)
        RowRewardWeighted = GetWeight(v)
    SmoothedR=[]
    for i in range(len(RowRewardWeighted)):
        SmoothedR.append(Alpha*RowRewardWeighted[i]+(1-Alpha)*Rep[i])
    return({'FirstL':FirstLoading, 'OldRep':Rep, 'ThisRep':RowRewardWeighted, 'Smoothrep':SmoothedR})

m=[[1,0,1,0],[1,0,1,0],[1,0,0,1]]
GetRewardWeights(m, Rep=[1,1,1])
