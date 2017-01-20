from node import Node, EndNode
from Person import Person
import sys

class Graph:
    def __init__(self,startNode,endNode, nodeList):
        self.startNode = startNode
        self.endNode = endNode
        self.nodeList = nodeList #list of nodes from end to start
        endNode.graph = self

    def addPerson(self):
        p = Person()
        p.startWaiting()
        self.startNode.addToQueue(p)

    def simulate(self,numPeople):
        #start all the threads
        for node in self.nodeList:
            print(node, "adjacency list: ", node.adjacencyList)
            node.start()
        self.endNode.numPeople = numPeople
        for i in range(numPeople):
            self.addPerson()

    def finish(self):
        self.startNode.stop()
        sys.exit()

def getIndicesOfNum(num, twoDList):
    indices = []
    for i in range(0, len(twoDList)):
        for j in range(0, len(twoDList[i])):
            if(twoDList[i][j] == num):
                indices.append(i)
                break
    return indices

def makeGraph(numIDcheckNodes, numScanners, numAITS, dropOffForAITS, idCheckToDropoff): #dropOffForAITS is a 2-d list of length numScanners that says which AIT(s) the scanner goes to (0 goes to 0 (or more) always)
    def probFunction():
        return 0
    # endNode = EndNode()
    # pickUpNode = Node(2, probFunction, [endNode], 100, "pickUp")
    # aitNode = Node(1.3, probFunction, [pickUpNode], 100, "ait")
    # dropOffNode = Node(2, probFunction, [aitNode], 100, "dropOff")
    # idCheckNode = Node(1.3, probFunction, [dropOffNode], 100, "idCheck")
    # startNode = Node(0, probFunction, [idCheckNode], 100, "start")
    # nodeList = [endNode, pickUpNode, aitNode, dropOffNode, idCheckNode, startNode]

    endNode = EndNode()
    pickUpNodeList = []
    for i in range(numScanners):
        pickUpNodeList.append(Node(2, probFunction, [endNode], 100, "pickUp" + str(i)))
    aitNodeList = []
    for i in range(numAITS):
        adjacencyList = []
        for i in getIndicesOfNum(i, dropOffForAITS):
            adjacencyList.append(pickUpNodeList[i])
        aitNodeList.append(Node(1.3, probFunction, adjacencyList, 100, "ait" + str(i)))
    dropOffNodeList = []
    for i in range(numScanners):
        adjacencyList = []
        for ait in dropOffForAITS[i]:
            adjacencyList.append(aitNodeList[ait])
        dropOffNodeList.append(Node(2, probFunction, adjacencyList, 20, "dropOff" + str(i)))
    idCheckNodeList = []
    for i in range(numIDcheckNodes):
        adjacencyList = []
        for idCheck in idCheckToDropoff[i]:
            adjacencyList.append(dropOffNodeList[idCheck])
        idCheckNodeList.append(Node(1.3, probFunction, adjacencyList, 1, "idCheck" + str(i)))
    startNode = Node(0, probFunction, idCheckNodeList, 100, "start")

    nodeList = [endNode]
    nodeList = nodeList + pickUpNodeList + aitNodeList + dropOffNodeList + idCheckNodeList
    nodeList.append(startNode)
    # for node in nodeList:
    #     node.start()

    g = Graph(startNode, endNode, nodeList)
    g.simulate(1)

    # p = Person()
    # p.startWaiting()
    # startNode.addToQueue(p)

makeGraph(1,1,1, [[0]], [[0]])



