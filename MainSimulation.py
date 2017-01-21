from node import Node, EndNode
from Person import Person
import sys
import time
from collections import namedtuple
import random

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
        #start all the threads
        for node in self.nodeList:
            print(node, "adjacency list: ", node.adjacencyList)
            node.start()
        self.endNode.numPeople = numPeople
        for i in range(numPeople):
            self.addPerson()
            time.sleep(self.generateRandomSeconds())

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

SecurityLevel = namedtuple("SecurityLevel", "numElements defaultConnections allConnections")

#def makeGraph(numIDcheckNodes, numScanners, numAITS, idCheckToDropoff, dropOffForAITS): #dropOffForAITS is a 2-d list of length numScanners that says which AIT(s) the scanner goes to (0 goes to 0 (or more) always)
def makeGraph(startLevel,idCheckLevel,dropOffLevel,aitLevel):
    # these must all be SecurityLevel named tuples
    def defaultChoiceFn(choicesList,default=0,prevPath=[]):
        return default
    def strictMinimumFn(choicesList,default=0,prevPath=[]):
        print("MINFUNC: ",choicesList,default)
        if len(choicesList) <= 1:
            return 0
        if choicesList[default] == min(choicesList):
            return default
        try:
            return choicesList.index(min(choicesList))
        except ValueError:
            print("Something is truly wrong here: the minimum element is not in the array...")
            return 0
    # endNode = EndNode()
    # pickUpNode = Node(2, defaultChoiceFn, [endNode], 100, "pickUp")
    # aitNode = Node(1.3, defaultChoiceFn, [pickUpNode], 100, "ait")
    # dropOffNode = Node(2, defaultChoiceFn, [aitNode], 100, "dropOff")
    # idCheckNode = Node(1.3, defaultChoiceFn, [dropOffNode], 100, "idCheck")
    # startNode = Node(0, defaultChoiceFn, [idCheckNode], 100, "start")
    # nodeList = [endNode, pickUpNode, aitNode, dropOffNode, idCheckNode, startNode]

    endNode = EndNode()
    pickUpNodeList = []
    for i in range(dropOffLevel.numElements):
        pickUpNodeList.append(Node(8.5, defaultChoiceFn, [endNode], 0, 100, "pickUp" + str(i)))

    aitNodeList = []
    for i in range(aitLevel.numElements):
        adjacencyList = []
        for j in getIndicesOfNum(i, dropOffLevel.allConnections):
            adjacencyList.append(pickUpNodeList[j])
        try:
            defaultIndex = dropOffLevel.defaultConnections.index(i)
        except ValueError:
            defaultIndex = 0 # the function must take care of it anyway
        aitNodeList.append(Node(11.5, defaultChoiceFn, adjacencyList, defaultIndex,  100, "ait" + str(i)))
    
    dropOffNodeList = []
    for i in range(dropOffLevel.numElements):
        adjacencyList = []
        for ait in dropOffLevel.allConnections[i]:
            adjacencyList.append(aitNodeList[ait])
        dropOffNodeList.append(Node(8.5, defaultChoiceFn, adjacencyList, dropOffLevel.defaultConnections[i], 20, "dropOff" + str(i)))
    
    idCheckNodeList = []
    for i in range(idCheckLevel.numElements):
        adjacencyList = []
        for dropOff in idCheckLevel.allConnections[i]:
            adjacencyList.append(dropOffNodeList[dropOff])
        idCheckNodeList.append(Node(11, defaultChoiceFn, adjacencyList, idCheckLevel.defaultConnections[i], 1, "idCheck" + str(i)))
    
    startNodeList = []
    for i in range(startLevel.numElements):
        adjacencyList = []
        for idCheck in startLevel.allConnections[i]:
            adjacencyList.append(idCheckNodeList[idCheck])
        startNodeList.append(Node(0, strictMinimumFn, adjacencyList, startLevel.defaultConnections[i], 100, "start" + str(i)))
  #  startNode = Node(0, defaultChoiceFn, idCheckNodeList, 0, 100, "start")
    


    nodeList = [endNode]
    nodeList = nodeList + pickUpNodeList + aitNodeList + dropOffNodeList + idCheckNodeList
    nodeList.extend(startNodeList)
    # for node in nodeList:
    #     node.start()

    g = Graph(startNodeList, endNode, nodeList)
    g.simulate(10000)

    # p = Person()
    # p.startWaiting()
    # startNode.addToQueue(p)

random.seed(a=1)

#be careful, the second argument is indexes of the elements of the third argument 
startLevel = SecurityLevel(2,[1,0],[[0,1], [2]])
idCheckTuple = SecurityLevel(3,[0,1,0],[[0,1], [0,1], [2]])
dropOffTuple = SecurityLevel(3,[0,1,0],[[0,1], [0,1], [2]])
aitTuple = SecurityLevel(3,None,None)

makeGraph(startLevel,idCheckTuple,dropOffTuple,aitTuple)
#makeGraph(2,3,3, #numIDCheckNodes, numScanners, numAITS
#          [[0,1], [1,2]], #idCheckToDropOff
#          [[0,1], [0,1,2], [2]]) #dropOffForAITS



