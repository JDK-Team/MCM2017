from node import Node, EndNode
from Person import Person
import sys
import time
from collections import namedtuple
import random
scalar = 100

class Graph:
    
    def __init__(self,startNodes,endNode,nodeList):
        self.startNodes = startNodes
        self.endNode = endNode
        self.nodeList = nodeList #list of nodes from end to start
        endNode.graph = self

    def addPerson(self):
        p = Person()
        p.startWaiting()
        s = 0
        if random.random() < 0.45:
            s += 1
        self.startNodes[s].addToQueue(p)

    def simulate(self,numPeople):
        global scalar
        #start all the threads
        for node in self.nodeList:
            print(node, "adjacency list: ", node.adjacencyList)
            node.start()
        self.endNode.numPeople = numPeople
        for i in range(numPeople):
            self.addPerson()
            time.sleep(self.generateRandomSeconds()/scalar)

    def finish(self):
        for startNode in self.startNodes:
            startNode.stop()
        sys.exit()

    @staticmethod
    def generateRandomSeconds():
        r = random.random()
        if r < .3913:
            return 1
        elif r < .543:
            return 5
        elif r < .696:
            return 10
        elif r < .826:
            return 15
        else:
            return 20

def getIndicesOfNum(num, twoDList):
    indices = []
    for i in range(0, len(twoDList)):
        for j in range(0, len(twoDList[i])):
            if(twoDList[i][j] == num):
                indices.append(i)
                break
    return indices

def isInt(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

SecurityLevel = namedtuple("SecurityLevel", "numElements defaultConnections allConnections zoneDConnections")

#def makeGraph(numIDcheckNodes, numScanners, numAITS, idCheckToDropoff, dropOffForAITS): #dropOffForAITS is a 2-d list of length numScanners that says which AIT(s) the scanner goes to (0 goes to 0 (or more) always)
def makeGraph(startLevel,idCheckLevel,dropOffLevel,aitLevel, preCheckNodes, numberOfZoneD):
    # these must all be SecurityLevel named tuples
    def defaultChoiceFn(choicesList,default=0,prevPath=[]):
        return default
    def strictMinimumFn(choicesList,default=0,prevPath=[]):
        #print("MINFUNC: ",choicesList,default)
        if len(choicesList) <= 1:
            return 0
        if choicesList[default] == min(choicesList):
            return default
        try:
            return choicesList.index(min(choicesList))
        except ValueError:
            print("Something is truly wrong here: the minimum element is not in the array...")
            return 0
    def zoneDChoiceFn(choicesList,default=0,prevPath=[]): #zoneD choices are always listed after regular screening choices (never choice 0)
        randNum = random.random()
        if(randNum<.01): #1% of people go to zone D and 1% of bags go to zone D
            if(len(choicesList) == 2):
                return 1
            return choicesList.index(min(choicesList)) #return index of zoneD with fewest people waiting
        else:
            return default
    def aitChoiceFn(choicesList,default=0,prevPath=[]): #go back to the scanner you came from or go to zone D
        randNum = random.random()
        if (randNum < .01):  # 1% of people go to zone D and 1% of bags go to zone D
            if (len(choicesList) == 2):
                return 1
            return choicesList.index(min(choicesList))  # return index of zoneD with fewest people waiting
        else:
            dropOffNode = prevPath[-2]
            startIndex = len(dropOffNode)-1
            for letter in range(len(dropOffNode)):
                if(isInt(dropOffNode[letter])):
                    startIndex = letter
                    break
            index = dropOffNode[startIndex:]
            return index

    # endNode = EndNode()
    # pickUpNode = Node(2, defaultChoiceFn, [endNode], 100, "pickUp")
    # aitNode = Node(1.3, defaultChoiceFn, [pickUpNode], 100, "ait")
    # dropOffNode = Node(2, defaultChoiceFn, [aitNode], 100, "dropOff")
    # idCheckNode = Node(1.3, defaultChoiceFn, [dropOffNode], 100, "idCheck")
    # startNode = Node(0, defaultChoiceFn, [idCheckNode], 100, "start")
    # nodeList = [endNode, pickUpNode, aitNode, dropOffNode, idCheckNode, startNode]

    global scalar

    endNode = EndNode()

    zoneDNodeList = []
    for i in range(numberOfZoneD):
        zoneDNodeList.append(Node(300/scalar, defaultChoiceFn, [endNode], 0, 10, "zoneD" + str(i))) #10 people can be in zone D

    pickUpNodeList = []
    for i in range(dropOffLevel.numElements):
        adjacencyList = [endNode]
        for j in dropOffLevel.zoneDConnections[i]:
            adjacencyList.append(zoneDNodeList[j])
        if(i in preCheckNodes):
            pickUpNodeList.append(Node(5/scalar, zoneDChoiceFn, adjacencyList, 0, 100, "PreCheckPickUp" + str(i)))
        else:
            pickUpNodeList.append(Node(8.5/scalar, zoneDChoiceFn, adjacencyList, 0, 100, "pickUp" + str(i)))

    aitNodeList = []
    for i in range(aitLevel.numElements):
        adjacencyList = []
        for j in getIndicesOfNum(i, dropOffLevel.allConnections):
            adjacencyList.append(pickUpNodeList[j])
        for j in aitLevel.zoneDConnections[i]:
            adjacencyList.append(zoneDNodeList[j])
        try:
            defaultIndex = dropOffLevel.defaultConnections.index(i)
        except ValueError:
            defaultIndex = 0 # the function must take care of it anyway
        aitNodeList.append(Node(11.5/scalar, aitChoiceFn, adjacencyList, defaultIndex,  100, "ait" + str(i)))
    
    dropOffNodeList = []
    for i in range(dropOffLevel.numElements):
        adjacencyList = []
        for ait in dropOffLevel.allConnections[i]:
            adjacencyList.append(aitNodeList[ait])
        if(i in preCheckNodes):
            dropOffNodeList.append(Node(5/scalar, defaultChoiceFn, adjacencyList, dropOffLevel.defaultConnections[i], 20, "PreCheckdropOff" + str(i)))
        else:
            dropOffNodeList.append(Node(8.5/scalar, defaultChoiceFn, adjacencyList, dropOffLevel.defaultConnections[i], 20, "dropOff" + str(i)))
    
    idCheckNodeList = []
    for i in range(idCheckLevel.numElements):
        adjacencyList = []
        for dropOff in idCheckLevel.allConnections[i]:
            adjacencyList.append(dropOffNodeList[dropOff])
        idCheckNodeList.append(Node(11/scalar, defaultChoiceFn, adjacencyList, idCheckLevel.defaultConnections[i], 1, "idCheck" + str(i)))
    
    startNodeList = []
    for i in range(startLevel.numElements):
        adjacencyList = []
        for idCheck in startLevel.allConnections[i]:
            adjacencyList.append(idCheckNodeList[idCheck])
        startNodeList.append(Node(0, strictMinimumFn, adjacencyList, startLevel.defaultConnections[i], 100, "start" + str(i)))
  #  startNode = Node(0, defaultChoiceFn, idCheckNodeList, 0, 100, "start")
    


    nodeList = [endNode]
    nodeList = nodeList + zoneDNodeList + pickUpNodeList + aitNodeList + dropOffNodeList + idCheckNodeList
    nodeList.extend(startNodeList)
    # for node in nodeList:
    #     node.start()

    g = Graph(startNodeList, endNode, nodeList)
    g.simulate(100)

    # p = Person()
    # p.startWaiting()
    # startNode.addToQueue(p)

random.seed(a=1)

#be careful, the second argument is indexes of the elements of the third argument 
startLevel = SecurityLevel(2,[1,0],[[0,1], [2]], None)
idCheckTuple = SecurityLevel(3,[0,1,0],[[0,1], [0,1], [2]], None)
dropOffTuple = SecurityLevel(3,[0,1,0],[[0,1], [0,1], [2]], [[0], [0], [1]]) #last argument is the zone D's that the given scanner feeds in to (should have the
                                                                                    #same number of sublists as there are scanners)
aitTuple = SecurityLevel(3,None,None, [[0],[0],[1]])
preCheckNodes = [2] #indices of drop off (and therefore pickup) nodes that are TSA-precheck

makeGraph(startLevel,idCheckTuple,dropOffTuple,aitTuple, preCheckNodes, 2)
#makeGraph(2,3,3, #numIDCheckNodes, numScanners, numAITS
#          [[0,1], [1,2]], #idCheckToDropOff
#          [[0,1], [0,1,2], [2]]) #dropOffForAITS



