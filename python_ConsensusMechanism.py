from numpy import dot

def DemocracyRep(X):
    v=[]
    for i in range(len(x)):
        v.append(1)
    Rep=custommath.ReWeight(v)
def GetRewardWeights(M, Rep=DemocracyRep(M), alpha=0.1):
    Results=WeightedPrinComp(M, Rep)
    FirstLoading=Results['Loadings']
    FirstScore=Results['Scores']
    Set1=FirstScore+abs(min(FirstScore))
    Set2=FirstScore-max(FirstScore)
    Old=dot(Rep,M)
    New1=custommath.GetWeight(dot(Set1,M))
    New2=custommath.GetWeight(dot(Set2,M))
    RefInd = sum( (New1-Old)**2) -  sum( (New2-Old)**2)
    if(RefInd<=0): AdjPrinComp = Set1  
    else: AdjPrinComp = Set2  
    RowRewardWeighted=Rep
    if(max(abs(AdjPrinComp))!=0):
        RowRewardWeighted=custommath.GetWeight(map(lamda x: x* (Rep/mean(Rep)), AdjPrinComp))
    SmoothedR = Alpha*RowRewardWeighted + (1-Alpha)*Rep
    Out = {"FirstL":FirstLoading, "OldRep":Rep.T, "ThisRep":RowRewardWeighted, "SmoothRep":SmoothedR}  
    return(Out)

