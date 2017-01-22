

#four one pre
def defaultFourLanes():
    startLevel = SecurityLevel(2,[1,0],[[0,1],[2]],None)
    idCheckLevel = SecurityLevel(3,[1,1,0],[[0,1,2],[0,1,2],[0,1,2],[3]],None)
    dropOffTuple = SecurityLevel(4,[0,1,0,0],[[0,1],[0,1],[2],[3]],[[0],[0],[1],[1]])
    aitTuple = SecurityLevel(4,None,None,None)
    numBagChecks = 2
    return (startLevel,idCheckLevel,dropOffTuple,aitTuple,numBagChecks)



