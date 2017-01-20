from node import Node, EndNode
from Person import Person
import sys

class Graph:
    def __init__(self,startNode,endNode):
        self.startNode = startNode
        self.endNode = endNode
        endNode.graph = self

    def addPerson(self):
        p = Person()
        p.startWaiting()
        self.startNode.addToQueue(p)

    def simulate(self,numPeople):
        self.endNode.numPeople = numPeople
        for i in range(numPeople):
            self.addPerson()
    def finish(self):
        self.startNode.stop()
        sys.exit()

def makeGraph(numIDcheckNodes, numScanners, numAITS):
    def probFunction():
        return 0
    endNode = EndNode()
    pickUpNode = Node(2, probFunction, [endNode], 100, "pickUp")
    aitNode = Node(1.3, probFunction, [pickUpNode], 100, "ait")
    dropOffNode = Node(2, probFunction, [aitNode], 100, "dropOff")
    idCheckNode = Node(1.3, probFunction, [dropOffNode], 100, "idCheck")
    startNode = Node(0, probFunction, [idCheckNode], 100, "start")
    nodeList = [endNode, pickUpNode, aitNode, dropOffNode, idCheckNode, startNode]

    for node in nodeList:
        try:
            node.start()
        except(KeyboardInterrupt, SystemExit):
            sys.exit()

    g = Graph(startNode, endNode)
    g.simulate(1)

    # p = Person()
    # p.startWaiting()
    # startNode.addToQueue(p)

makeGraph(1,1,1)



