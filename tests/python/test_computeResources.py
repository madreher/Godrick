import os
from pathlib import Path
import pytest

from godrick.computeResources import ComputeCluster

def test_singleHost():

    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/singlehost.txt")
    cluster = ComputeCluster(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    assert cluster.getNbNodes() == 1

    node = cluster.getNodeByIndex(0)
    assert node.getNbSockets() == 1

    socket = node.getSocketByIndex(0)
    assert socket.hasHyperthreads() == True

    assert socket.getCoresIndexes() == [0, 1, 2, 3]
    assert socket.getHTIndexes() == [4, 5, 6, 7]

    assert cluster.toDict() == {'name': 'myCluster', 'nodes': [{'hostname': 'machine1', 'sockets': [{'mainthreads': [0, 1, 2, 3], 'hyperthreads': [4, 5, 6, 7], 'hostname': 'machine1', 'hasht': True}]}]}

def test_clusterNodeOutOfBound():
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/singlehost.txt")
    cluster = ComputeCluster(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)

    with pytest.raises(Exception) as e_info:
        node = cluster.getNodeByIndex(1)

def test_clusterSocketOutOfBound():
    exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/singlehost.txt")
    cluster = ComputeCluster(name="myCluster")
    cluster.initFromHostFile(exampleFile, True)
    node = cluster.getNodeByIndex(0)
    
    with pytest.raises(Exception) as e_info:
        socket = node.getSocketByIndex(1)