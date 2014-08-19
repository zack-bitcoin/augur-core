"""a python version of the R program at https://github.com/psztorc/Truthcoin
"""
import rpy2.robjects as robjects


robjects.r('''
#Consensus Mechanism
#This is the mechanism that, theoretically,
 #   1] allows the software to determine the state of Decisions truthfully, and
 #   2] only allows an efficient number of most-traded-upon-Decisions.


#To my knowledge, R does not feature 'automatic working directories' unless it is being run as a script

#CustomMath.r
#A collection of relatively basic functions.

MeanNA <- function(Vec) {
  #Replaces NA instances with their mean instead
  m <- mean(Vec, na.rm = TRUE)
  Vec[is.na(Vec)] <- m
  return(Vec)
}

GetWeight <- function(Vec,AddMean=FALSE) {
  #Takes a Vector, absolute value, then proportional linear deviance from 0.
  new <- abs(Vec)
  if(AddMean==1) new  <- new + mean(new)
  if(sum(new)==0) new <- new + 1
  new <- new/sum(new)
  return(new)
}

Catch <- function(X,Tolerance=0) {
  #x is the ConoutRAW numeric, Tolerance is the length of the midpoint corresponding to .5 
  #The purpose here is to handle rounding for binary contracts
  
  #This function must be substantially altered to support scaled contracts.
  
  if(X<(.5-(Tolerance/2))) return(0)
  else if(X>(.5+(Tolerance/2))) return(1)
  else return(.5)
  
}


GetModes <- function(X, Weights) {
#   ModeCalc <- as.numeric(  names( which.max( table(X)) ) )
#   
#   TopThree <- sort( table(X), decreasing=TRUE)[1:3]
  
  Tab <- aggregate(x=Weights, by= list(X), FUN='sum')
  SortedTab <- Tab[order(Tab[,2], decreasing=TRUE),]
  
  TopThree <- SortedTab[1:3,1]
  
  return(TopThree)
}



weighted.median <- function(x, w, na.rm=TRUE, ties=NULL) {
  # Thanks to https://stat.ethz.ch/pipermail/r-help/2002-February/018614.html
  if (missing(w))
    w <- rep(1, length(x));
  
  # Remove values that are NA's
  if (na.rm == TRUE) {
    keep <- !(is.na(x) | is.na(w));
    x <- x[keep];
    w <- w[keep];
  } else if (any(is.na(x)))
    return(NA);
  
  # Assert that the weights are all non-negative.
  if (any(w < 0))
    stop("Some of the weights are negative; one can only have positive
         weights.");
  
  # Remove values with weight zero. This will:
  #  1) take care of the case when all weights are zero,
  #  2) make sure that possible tied values are next to each others, and
  #  3) it will most likely speed up the sorting.
  n <- length(w);
  keep <- (w > 0);
  nkeep <- sum(keep);
  if (nkeep < n) {
    x <- x[keep];
    w <- w[keep];
    n <- nkeep;
  }
  
  # Are any weights Inf? Then treat them with equal weight and all others
  # with weight zero.
  wInfs <- is.infinite(w);
  if (any(wInfs)) {
    x <- x[wInfs];
    n <- length(x);
    w <- rep(1, n);
  }
  
  # Are there any values left to calculate the weighted median of?
  if (n == 0)
    return(NA);
  
  # Order the values and order the weights accordingly
  ord <- order(x);
  x <- x[ord];
  w <- w[ord];
  
  wcum <- cumsum(w);
  wsum <- wcum[n];
  wmid <- wsum / 2;
  
  # Find the position where the sum of the weights of the elements such that
  # x[i] < x[k] is less or equal than half the sum of all weights.
  # (these two lines could probably be optimized for speed).
  lows <- (wcum <= wmid);
  k  <- sum(lows);
  
  # Two special cases where all the weight are at the first or the
  # last value:
  if (k == 0) return(x[1]);
  if (k == n) return(x[n]);
  
  # At this point we know that:
  #  1) at most half the total weight is in the set x[1:k],
  #  2) that the set x[(k+2):n] contains less than half the total weight
  # The question is whether x[(k+1):n] contains *more* than
  # half the total weight (try x=c(1,2,3), w=c(1,1,1)). If it is then
  # we can be sure that x[k+1] is the weighted median we are looking
  # for, otherwise it is any function of x[k:(k+1)].
  
  wlow  <- wcum[k];    # the weight of x[1:k]
  whigh <- wsum - wlow;  # the weight of x[(k+1):n]
  if (whigh > wmid)
    return(x[k+1]);
  
  if (is.null(ties) || ties == "weighted") {  # Default!
    (wlow*x[k] + whigh*x[k+1]) / wsum;
  } else if (ties == "max") {
    x[k+1];
  } else if (ties == "min") {
    x[k];
  } else if (ties == "mean") {
    (x[k]+x[k+1])/2;
  } else if (ties == "both") {
    c(x[k], x[k+1]);
  }
}

Rescale <- function(UnscaledMatrix, ScalingData) {
  #Calulate multiplicative factors
  InvSpan = ( 1/ ( ScalingData["Max",] - ScalingData["Min",]) )
  
  #Recenter
  OutMatrix <- sweep(UnscaledMatrix, 2, ScalingData["Min",])
  
  #Rescale
  NaIndex <- is.na(OutMatrix) #NA-Preempt
  OutMatrix[NaIndex] <- 0
  OutMatrix <- OutMatrix %*% diag(InvSpan)
  OutMatrix[NaIndex] <- NA #Restore NA's
  
  #Relabel
  row.names(OutMatrix) <- row.names(UnscaledMatrix)
  colnames(OutMatrix) <- colnames(UnscaledMatrix)
  
  return(OutMatrix)
}


Influence  <- function(Weight) {
  #Takes a normalized Vector (one that sums to 1), and computes relative strength of the indicators.
  #this is because by-default the conformity of each Author and Judge is expressed relatively.
  Expected <- rep(1/length(Weight),length(Weight))
  return( Weight / Expected)
}

ReWeight <- function(Vec,exclude=is.na(Vec)) {
  #Get the relative influence of numbers, treat NA as influence-less
  out <- Vec
  out[exclude] <- 0
  out <- out/sum(out)
  return(out)
}

ReverseMatrix <- function(Mat) {
  #Inverts a binary matrix
  return((Mat-1)*-1)
}

WeightedPrinComp <- function(X,Weights=ReWeight(rep(1,nrow(M))) ) {
  #Manually computes the statistical procedure known as Principal Components Analysis (PCA)
  #This version of the procedure is so basic, that it can also be thought of as merely a singular-value decomposition on a weighted covariance matrix.
  
  wCVM <- cov.wt(x=X,wt=Weights)
  
  L <- svd(wCVM$cov)$u[,1]
  S <- as.vector(scale(X,center=wCVM$center,scale= FALSE) %*% L)
  
  Out <- list("Scores"=S,"Loadings"=L)
  return(Out)
}
#Custom math end

AsMatrix <- function(Vec) return(matrix(Vec,nrow=length(Vec)))

# #Function Library
GetRewardWeights <- function(M,Rep=NULL,alpha=.1,Verbose=FALSE) {
  #Calculates the new reputations using WPCA
  
  if(is.null(Rep)) { Rep <- ReWeight(rep(1,nrow(M)))  ;   if(Verbose) print("Reputation not provided...assuming equal influence.")  }
  
  if(Verbose) {
    print("****************************************************")
    print("Begin 'GetRewardWeights'")
    print("Inputs...")
    print("Matrix:")
    print(M)
    print("")
    print("Reputation:")
    print(AsMatrix(Rep))
    print("")
  }

  #Rep=ReWeight(rep(1,nrow(M)))
  Results <- WeightedPrinComp(M,Rep)
  
  
  FirstLoading <- Results$Loadings #The first loading is designed to indicate which Decisions were more 'agreed-upon' than others. 
  FirstScore   <- Results$Scores   #The scores show loadings on consensus (to what extent does this observation represent consensus?)
  
  if(Verbose) { print("First Loading:"); print(FirstLoading); print("First Score:"); print(AsMatrix(FirstScore)) }
  
  #PCA, being an abstract factorization, is incapable of determining anything absolute.
  #Therefore the results of the entire procedure would theoretically be reversed if the average state of Decisions changed from TRUE to FALSE.
  #Because the average state of Decisions is a function both of randomness and the way the Decisions are worded, I quickly check to see which
  #  of the two possible 'new' reputation vectors had more opinion in common with the original 'old' reputation.
  #  I originally tried doing this using math but after multiple failures I chose this ad hoc way.
  Set1 <-  FirstScore+abs(min(FirstScore))
  Set2 <-  FirstScore-max(FirstScore)   
  
  Old <- Rep%*%M
  
  New1 <- GetWeight(Set1%*%M)
  New2 <- GetWeight(Set2%*%M)
  
  #Difference in Sum of squared errors, if >0, then New1 had higher errors (use New2), and conversely if <0 use 1.
  RefInd <- sum( (New1-Old)^2) -  sum( (New2-Old)^2)
  
  if(RefInd<=0) AdjPrinComp <- Set1  
  if(RefInd>0)  AdjPrinComp <- Set2  
  
  if(Verbose) {
    print("")
    print("Estimations using: Previous Rep, Option 1, Option 2")
    print( cbind( AsMatrix(Old), AsMatrix(New1), AsMatrix(New2) ) )
    print("")
    print("Previous period reputations, Option 1, Option 2, Selection")
    print( cbind( AsMatrix(Rep), AsMatrix(Set1), AsMatrix(Set2), AsMatrix(AdjPrinComp) ) )
  }
  
  #Declared here, filled below (unless there was a perfect consensus).
  RowRewardWeighted <- Rep # (set this to uniform if you want a passive diffusion toward equality when people cooperate [not sure why you would]). Instead diffuses towards previous reputation (Smoothing does this anyway).
  if(max(abs(AdjPrinComp))!=0) RowRewardWeighted <- GetWeight( (AdjPrinComp * Rep/mean(Rep)) ) #Overwrite the inital declaration IFF there wasn't perfect consensus.
  #note: Rep/mean(Rep) is a correction ensuring Reputation is additive. Therefore, nothing can be gained by splitting/combining Reputation into single/multiple accounts.
  
  
  #Freshly-Calculated Reward (Reputation) - Exponential Smoothing
  #New Reward: RowRewardWeighted
  #Old Reward: Rep
  SmoothedR <- alpha*(RowRewardWeighted) + (1-alpha)*Rep
  
  if(Verbose) {
    print("")
    print("Corrected for Additivity , Smoothed _1 period")
    print( cbind( AsMatrix(RowRewardWeighted), AsMatrix(SmoothedR)) )
  }
  
  #Return Data
  Out <- list("FirstL"=FirstLoading,"OldRep"=Rep,"ThisRep"=RowRewardWeighted,"SmoothRep"=SmoothedR)  #Keep the factors and time information along for the ride, they are interesting.
  return(Out)
}

GetDecisionOutcomes <- function(Mtemp, Rep, ScaledIndex, Verbose=FALSE) {
  #Determines the Outcomes of Decisions based on the provided reputation (weighted vote)
  
  if(missing(Rep)) { Rep <- ReWeight(rep(1,nrow(Mtemp)))  ;   if(Verbose) print("Reputation not provided...assuming equal influence.")  }
  
  if(Verbose) { print("****************************************************") ; print("Begin 'GetDecisionOutcomes'")}
  
  RewardWeightsNA <- Rep
  
  DecisionOutcomes.Raw  <- 1:ncol(Mtemp) #Declare this (filled below)
  
  for(i in 1:ncol(Mtemp)) {    
    #For each column:    
    Row <- ReWeight(RewardWeightsNA[!is.na(Mtemp[,i])]) #The Reputation of the row-players who DID provide judgements, rescaled to sum to 1.
    Col <- Mtemp[!is.na(Mtemp[,i]),i]                   #The relevant Decision with NAs removed. ("What these row-players had to say about the Decisions they DID judge.")
    
    #Discriminate Based on Contract Type
    if(!ScaledIndex[i]) DecisionOutcomes.Raw[i] <- Row%*%Col                     #Our Current best-guess for this Binary Decision (weighted average) 
    if(ScaledIndex[i]) DecisionOutcomes.Raw[i] <- weighted.median(w=Row, x=Col)  #Our Current best-guess for this Scaled Decision (weighted median)
   
    if(Verbose) { print("** **"); print("Column:"); print(i); print(AsMatrix(Row)); print(Col); print("Consensus:"); print(DecisionOutcomes.Raw[i])}
  }
  
  #Output
  return(DecisionOutcomes.Raw)
}

FillNa <- function(Mna, Rep, ScaledIndex, CatchP=.1, Verbose=FALSE) { 
  #Uses exisiting data and reputations to fill missing observations.
  #Essentially a weighted average using all availiable non-NA data.
  #How much should slackers who arent voting suffer? I decided this would depend on the global percentage of slacking.
  
  if(missing(Rep)) { Rep <- ReWeight(rep(1,nrow(Mna)))  ;   if(Verbose) print("Reputation not provided...assuming equal influence.")  }
  
  Mnew <- Mna #Declare (in case no Missing values, Mnew, MnewC, and Mna will be the same)
  MnewC <- Mna
  
  if(sum(is.na(Mna))>0) {
    #Of course, only do this process if there ARE missing values.
    
    if(Verbose) print("Missing Values Detected. Beginning presolve using availiable values.")
    
    #Decision Outcome - Our best guess for the Decision state (FALSE=0, Ambiguous=.5, TRUE=1) so far (ie, using the present, non-missing, values).
    DecisionOutcomes.Raw <- GetDecisionOutcomes(Mna,Rep,ScaledIndex,Verbose)
    
    #Fill in the predictions to the original M
    NAmat <- is.na(Mna)   #Defines the slice of the matrix which needs to be edited.
    Mnew[NAmat] <- 0       #Erase the NA's
       
    #Slightly complicated:
    NAsToFill <- ( NAmat%*%diag(as.vector(DecisionOutcomes.Raw)) )
    #   This builds a matrix whose columns j:
        #          NAmat was false (the observation wasn't missing)     ...  have a value of Zero
        #          NAmat was true (the observation was missing)         ...  have a value of the jth element of DecisionOutcomes.Raw (the 'current best guess') 
    Mnew <- Mnew + NAsToFill
    #This replaces the NAs, which were zeros, with the predicted Decision outcome.
    
    
    if(Verbose) { print("Missing Values:"); print(NAmat) ; print("Imputed Values:"); print(NAsToFill)}
    
    #Declare Output
    MnewC <- Mnew
    ## Discriminate based on contract type
    #Fill ONLY Binary contracts by appropriately forcing predictions into their discrete (0,.5,1) slot. (reveals .5 coordination, continuous variables are more gameable).
    MnewC[,!ScaledIndex] <- apply(Mnew[,!ScaledIndex], c(1,2), function(x) Catch(x,CatchP) )
    #
    
  
  }
  
  if(Verbose) { print("Raw Results:"); print(Mnew) ; print("Binned:"); print(MnewC) ; print("*** ** Missing Values Filled ** ***") }
  
  return(MnewC)
}


#Putting it all together:
Factory <- function(M0,Scales,Rep,CatchP=.1,MaxRow=5000,Verbose=FALSE) {
  #Main Routine
  #Fill the default reputations (egalitarian) if none are provided...unrealistic and only for testing.
  if(missing(Rep)) { Rep <- ReWeight(rep(1,nrow(M0)))
                     if(Verbose) print("Reputation not provided...assuming equal influence.")
  }
  
  #******************
  #Fill the default scales (binary) if none are provided. In practice, this would also never be used.
  if(missing(Scales)) { Scales <- matrix( c( rep(FALSE,ncol(M0)),
                                             rep(0,ncol(M0)),
                                             rep(1,ncol(M0))), 3, byrow=TRUE, dimnames=list(c("Scaled","Min","Max"),colnames(M0)) )
                        if(Verbose) print("Scales not provided...assuming binary (0,1).")
  }
  ScaledIndex=as.logical( Scales["Scaled",] )
  
  MScaled <- Rescale(M0, Scales)

  #******************
  
  #Handle Missing Values  
  Filled <- FillNa(MScaled, Rep, ScaledIndex, CatchP, Verbose)

  ## Consensus - Row Players 
  #New Consensus Reward
  PlayerInfo <- GetRewardWeights(Filled,Rep,.1,Verbose)
  AdjLoadings <- PlayerInfo$FirstL
  
  ##Column Players (The Decision Creators)
  # Calculation of Reward for Decision Authors
  # Consensus - "Who won?" Decision Outcome 
  DecisionOutcomes.Raw <- PlayerInfo$SmoothRep %*% Filled #Declare (all binary), Simple matrix multiplication ... highest information density at RowBonus, but need DecisionOutcomes.Raw to get to that
  for(i in 1:ncol(Filled)) {    #slow implementation.. 'for loop' bad on R, much faster on python
    #Discriminate Based on Contract Type
    if(ScaledIndex[i]) DecisionOutcomes.Raw[i] <- weighted.median(Filled[,i], w=PlayerInfo$SmoothRep)  #Our Current best-guess for this Scaled Decision (weighted median)
  }
  
  #The Outcome Itself
  #Discriminate Based on Contract Type
  DecisionOutcome.Final <- mapply(Catch,DecisionOutcomes.Raw,Tolerance=CatchP) #Declare first (assumes all binary) 
  DecisionOutcome.Final[ScaledIndex] <- DecisionOutcomes.Raw[ScaledIndex]      #Replace Scaled with raw (weighted-median)
  DecisionOutcome.Final <- t( Scales["Max",] - Scales["Min",] ) %*% diag( DecisionOutcome.Final )    #Rescale these back up.
  DecisionOutcome.Final <- DecisionOutcome.Final + Scales["Min",]                                        #Recenter these back up.
  
  # Quality of Outcomes - is there confusion?
  Certainty <- vector("numeric",ncol(Filled))
  #Discriminate Based on Contract Type
  # Scaled first:
  DecisionOutcome.Final
  for(i in 1:ncol(Filled)) { #For each Decision
    Certainty[i] <- sum( PlayerInfo$SmoothRep [ DecisionOutcomes.Raw[i] == Filled[,i] ] )  # Sum of, the reputations which, met the condition that they voted for the outcome which was selected for this Decision.
  }
  # Overwrite Binary:
  Certainty[!ScaledIndex] <- abs(2*(DecisionOutcomes.Raw[!ScaledIndex]-.5))    # .5 is obviously undesireable for binaries, this function travels from 0 to 1 with a minimum at .5
  ConReward <- GetWeight(Certainty)                  #Grading Authors on a curve. -not necessarily the best idea? may just use Certainty instead
  Avg.Certainty <- mean(Certainty)                   #How well did beliefs converge?
  
 
  if(Verbose) {
    print("*Decision Outcomes Sucessfully Calculated*")
    print("Raw Outcomes, Certainty, AuthorPayoutFactor"); print( cbind(DecisionOutcomes.Raw,Certainty,ConReward))
  }
  
  
  ## Participation
  
  #Information about missing values
  NAmat <- M0*0 
  NAmat[is.na(NAmat)] <- 1 #indicator matrix for missing
  
  #Participation Within Decisions (Columns) 
  # % of reputation that answered each Decision
  ParticipationC <- 1-(PlayerInfo$SmoothRep%*%NAmat)
  
  #Participation Within Agents (Rows) 
  # Many options
  
  # 1- Democracy Option - all Decisions treated equally.
  ParticipationR  <- 1-( apply(NAmat,1,sum)/ncol(M0) )
  
  #General Participation
  PercentNA <- 1-mean(ParticipationC)
  #(Possibly integrate two functions of participation?) Chicken and egg problem...
  
  if(Verbose) {
    print("*Participation Information*")
    print("Voter Turnout by question"); print( ParticipationC )
    print("Voter Turnout across questions"); print ( ParticipationR )
  }
  
  ## Combine Information
  #Row
  NAbonusR <- GetWeight(ParticipationR)
  RowBonus <- (NAbonusR*(PercentNA))+(PlayerInfo$SmoothR*(1-PercentNA))
  
  #Column
  NAbonusC <- GetWeight(ParticipationC)
  ColBonus <- (NAbonusC*(PercentNA))+(ConReward*(1-PercentNA))  
  
  #Present Results
  Output <- vector("list",6) #Declare
  names(Output) <- c("Original","Filled","Agents","Decisions","Participation","Certainty")
  
  Output[[1]] <- M0
  Output[[2]] <- Filled
  Output[[3]] <- cbind(PlayerInfo$OldRep, PlayerInfo$ThisRep,PlayerInfo$SmoothRep,apply(NAmat,1,sum),ParticipationR,NAbonusR,RowBonus)
  colnames(Output[[3]]) <- c("OldRep", "ThisRep", "SmoothRep", "NArow", "ParticipationR","RelativePart","RowBonus")   
  Output[[4]] <- rbind(AdjLoadings,DecisionOutcomes.Raw,ConReward,Certainty,apply(NAmat,2,sum),ParticipationC,ColBonus,DecisionOutcome.Final)
  rownames(Output[[4]]) <- c("First Loading","DecisionOutcomes.Raw","Consensus Reward","Certainty","NAs Filled","ParticipationC","Author Bonus","DecisionOutcome.Final")
  Output[[5]] <- (1-PercentNA) #Using this to set inclusion fees.
  Output[[6]] <- Avg.Certainty #Using this to set Catch Parameter
  
  return(Output)
}

#Long-Term
Chain <- function(X,Scales,N=2,ThisRep) {
  #Repeats factory process N times
  if(missing(ThisRep)) ThisRep <- ReWeight(rep(1,nrow(X)))
  
  if(missing(Scales)) { Scales <- matrix( c( rep(FALSE,ncol(X)),
                                             rep(0,ncol(X)),
                                             rep(1,ncol(X))), 3, byrow=TRUE, dimnames=list(c("Scaled","Min","Max"),colnames(X)) )
  }
  
  Output <- vector("list")
  for(i in 1:N) {
    Output[[i]] <- Factory(X,Scales,Rep=ThisRep)
    ThisRep <- Output[[i]]$Agents[,"RowBonus"]
  }
  
  return(Output)
}


#Notes

#Voting Across Time
#Later Votes could count more
#! ...simple change = DecisionOutcome.Final becomes exponentially smoothed result of previous chains.
#! require X number of chains (blocks) before the outcome is officially determined .. or, continue next round if ~ .5, or Decisions.Raw is within a threshold ( .2 to .8)
# Would need:
# 1] Percent Voted
# 2] Time Dimension of blocks.
''')

def matrix_to_r(m):
    lis=[]
    for i in m: lis+=i
    return make_matrix(lis, len(m[0]), len(m))

def make_matrix(lis, num_of_voters, num_of_decisions):
    list_string='('
    for i in lis:
        list_string+=str(i)
        list_string+=', '
    list_string=list_string[:-2]
    list_string+=')'
    string='''
B=matrix(
c'''+list_string+''',
nrow='''+str(num_of_voters)+''',
ncol='''+str(num_of_decisions)+''')

'''
    robjects.r(string)
    return(robjects.globalenv['B'])
'''
def string_to_vector(number_of_decisions, string, out):
    if number_of_decisions==0: 
        out.reverse()
        return
    out.append(float(string[-9:]))
    string_to_vector(number_of_decisions-1, string[:-10], out)
'''
def string_to_vector(number_of_decisions, string):
    out=string[23:].split(' ')
    out=filter(lambda s: s!='', out)
    return out

Factory=robjects.globalenv['Factory']
def main(m):
    #len(m) is the number of decisions.
    a=matrix_to_r(m)
    a=Factory(a)
    a=str(a).splitlines()
    outcome=string_to_vector(len(m), a[-8:-7][0])
    author_bonus=string_to_vector(len(m), a[-9:-8][0])
    participationc=string_to_vector(len(m), a[-10:-9][0])
    certaintyc=string_to_vector(len(m), a[-12:-11][0])
    agents=[]
    row_bonus=[]
    for i in range(len(m[0])):
        agents=[a[-19-i:-18-i][0]]+agents
    smoothrep=[]
    for agent in agents:
        smoothrep.append(agent[-48:-44])
        row_bonus.append(agent[-9:])
    return {'outcome':outcome,
            'author_bonus':author_bonus,
            'participation':participationc,
            'certainty':certaintyc,
            'votecoin_bonus_for_voters':smoothrep,
            'truthcoin_bonus_for_voters':row_bonus}

#m=[['NA',0,0],[0,1,0],[0,0,1],[0,0,0]]
#print(main(m))
