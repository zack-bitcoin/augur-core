import copy, numpy
def AsMatrix(v):
    #turns a vector into a 1-col matrix
    return map(lambda i: [i], v)
def mean(v): return sum(v)*1.0/len(v)
def replace_na(x, m):
    if type(x) in [int, float]:
        return x
    return m
def GetWeight(Vec, AddMean=False):
    print('Vec: ' +str(Vec))
    new=map(abs, Vec)
    m=mean(new)
    tot=sum(new)
    if AddMean: new=map(lambda x: x+m, new)
    if(tot==0): new=map(lambda x: x+1, new)
    new=map(lambda x: x/sum(new), new)
    return new
def Catch(X, Tolerance=0):
    if X<(0.5+(Tolerance/2)): return 1
    return 0.5
def median_walker(so_far_w, limit, x, w, prev_x):
    if so_far_w>limit: return prev_x
    if so_far_w==limit: return mean([1.0*prev_x, x[0]])
    return median_walker(so_far_w+w[0], limit, x[1:], w[1:], x[0])
def weighted_median(x, w):
    x, w=zip(*sorted(zip(x, w)))
    return median_walker(0, sum(w)*1.0/2, x, w, x[0])
def switch_row_cols(m):
    out=[]
    for i in range(len(m[0])):
        newrow=[]
        for row in m:
            newrow.append(row[i])
        out.append(newrow)
    return out
def MeanNA(v):
    vf=filter(lambda x: type(x) in [int, float], v)
    m=mean(vf)
    return map(lambda x: replace_na(x, m), v)
def Rescale(UnscaledMatrix):
    flipped_m=switch_row_cols(UnscaledMatrix)
    out=[]
    for row in flipped_m:
        mrow=MeanNA(copy.deepcopy(row))
        ma=max(mrow)
        mi=min(mrow)
        print('row: ' +str(row))
        out.append(map(lambda x: 'NA' if type(x)==str else (x-mi)/(ma-mi), row))
    return switch_row_cols(out)
def rescale_test():
    m=[[1, 1, 0, 0, 233, 16027.59],
       [1, 0, 0, 0, 199, 'NA'],
       [1, 1, 0, 0, 233, 16027.59],
       [1, 1, 1, 0, 250, 'NA'],
       [0, 0, 1, 1, 435, 8001.00],
       [0, 0, 1, 1, 435, 19999.00]]
    print(Rescale(m))
def Influence(Weight):
    l=len(Weight)
    return map(lambda x: x*l, Weight)
def ReWeight(v):
    w=map(lambda x: 0 if type(x)==str else x, v)
    s=sum(w)
    return map(lambda x: x*1.0/s, w)
def WeightedCov(Mat,Rep=-1):
    """Takes 1] a masked array, and 2] an [n x 1] dimentional array of weights, and computes the weighted covariance
    matrix and center of a given array.
    Taken from http://stats.stackexchange.com/questions/61225/correct-equation-for-weighted-unbiased-sample-covariance"""
    if type(Rep) is int:
        Rep = DemocracyCoin(Mat)
    
    Coins = copy.deepcopy(Rep)
    for i in range(len(Rep)):
        Coins[i] = (int( (Rep[i] * 1000000) )) 
    Mean = numpy.ma.average(Mat, axis=0, weights=numpy.hstack(Coins)) # Computing the weighted sample mean (fast, efficient and precise)
    XM = numpy.matrix( Mat-Mean ) # xm = X diff to mean
    #XM = numpy.matrix( map(lambda l: map(lambda x:x-Mean, l), Mat)) # xm = X diff to mean
    sigma2 = numpy.matrix( 1/(sum(Coins)-1) * numpy.dot(switch_row_cols(numpy.ma.multiply(XM, AsMatrix(Coins))), XM) ); # Compute the unbiased weighted sample covariance

    return( {'Cov':numpy.array(sigma2), 'Center':numpy.array(XM) } )
#print(WeightedCov([[1,0,1,0,1],[0,0,1,0,0],[0,0,0,0,0]],[100,1,1]))
def WeightedPrinComp(M, Weights):
    if len(Weights)!=len(M):
        print('Weights must be equal in length to rows')
        return 'error'
    wCVM=WeightedCov(M, Weights)
    print('wCVM: ' +str(wCVM))
    SVD=numpy.linalg.svd(wCVM['Cov'])
    L=SVD[0]
    #S=numpy.dot(scale(M, center=wCVM['Center'], scale=False), L)
    S=switch_row_cols(numpy.dot(wCVM['Center'], L))[0]
    return{'Scores':S, 'Loadings':L}
