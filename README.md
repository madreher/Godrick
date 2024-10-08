# Godrick

[![Godrick CI/CD](https://github.com/madreher/Godrick/actions/workflows/ci.yml/badge.svg)](https://github.com/madreher/Godrick/actions/workflows/ci.yml)
[![Coverage badge](https://raw.githubusercontent.com/madreher/Godrick/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/madreher/Godrick/blob/python-coverage-comment-action-data/htmlcov/index.html)
[![CPP Coverage Status](https://coveralls.io/repos/github/madreher/Godrick/badge.svg?branch=main)](https://coveralls.io/github/madreher/Godrick?branch=main)

## TLDR

Godrick is an in-situ middlware aiming at coupling HPC simulation codes with analysis and services, whether it be on the same compute environement or on remote resources connecting to the flow of data.

Ruinning a Godrick workflow is done in two steps. First, the user needs to declare a workflow via a Python API. This will generate the necessary configuration files to execute the workflow. Here is a simple example with two tasks taken from the `examples/mpibroadcast` folder. In this example, the goal is to broadcast a message from a single sender to a parallel receiver.
```
from godrick.workflow import Workflow
from godrick.task import MPITask, MPIPlacementPolicy
from godrick.launcher import MainLauncher
from godrick.computeResources import ComputeCollection
from godrick.communicator import MPIPairedCommunicator

import os
from pathlib import Path

# Declare the computational resources available for the workflow
exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/localhost.txt")
cluster = ComputeCollection(name="myCluster")
cluster.initFromHostFile(exampleFile, True)

# Split the cluster into 2 parts, one for each task
partitions = cluster.splitNodesByCoreRange([1, 3])

# Declare the sender and receiver, assigning them their respective resources, and declaring their ports to be able to send and receive data respectively
workflow = Workflow("MPIBroadcastWorkflow")
task1 = MPITask(name="send", cmdline="bin/send --name send --config config.MPIBroadcastWorkflow.json", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
task1.addOutputPort("out")
task1.setResources(partitions[0])
task2 = MPITask(name="receive", cmdline="bin/receive --name receive --config config.MPIBroadcastWorkflow.json", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
task2.addInputPort("in")
task2.setResources(partitions[1])

# Declare the communication channels between the different ports
comm1 = MPIPairedCommunicator("myComm")
comm1.connectToInputPort(task2.getInputPort("in"))
comm1.connectToOutputPort(task1.getOutputPort("out"))

workflow.declareTask(task1)
workflow.declareTask(task2)
workflow.declareCommunicator(comm1)

# Everything is declared, the MainLauncher object can be created to generate the necessary inputs.
launcher = MainLauncher()
launcher.generateOutputFiles(workflow=workflow)
```

Once this is done, configuration files will be generated in the current folder, including a launch script.
On the runtime side, here is a code snipet of the sender to be able to send data:
```
#include <godrick/mpi/godrickMPI.h>
#include <conduit/conduit.hpp>

// Initialize Godrick and load the workflow configuration
auto handler = godrick::mpi::GodrickMPI();
if(!handler.initFromJSON(configFile, taskName))    
{
    spdlog::error("Something went wrong during the workflow configuration.");
    exit(-1);
}

// Building the data to send with Conduit
conduit::Node data;
uint32_t val = 10;
data["data"] = val;

// Sending the data
if(handler.push("out", data))
    spdlog::info("Data sent from the send task.");
else
    spdlog::error("Something went wrong when sending the data.");

// We are done, closing the workflow
handler.close();

```

For more information, please refer to the rest of the documentation and examples in the `examples` folder.

## Installation on Ubuntu 

### Package dependencies 

These are packages taken from the official repo and should be fairly portable accross various distributions.

```
sudo apt install -y openmpi-bin \
    libopenmpi-dev \
    cmake \
    lcov \
    lsb-release \
    git \ 
    build-essential \
    python3-pip \
    git
```

### Conduit installation 

Godrick relies on [Conduit](https://llnl-conduit.readthedocs.io/en/latest/index.html) as its data model in order to send data between parallel tasks. 
Unfortunately, Conduit is not currently available as a package and has to be compiled manually. He is an example on how to compile Conduit. Please refer to Conduit documentation for more information if need.

```
# Adjust these variables to your own setup
export CONDUIT_PREFIX=$HOME/.local
export CONDUIT_SOURCE_DIR=$HOME/dev/conduit

mkdir -p $CONDUIT_SOURCE_DIR
cd $CONDUIT_SOURCE_DIR
git clone --recursive https://github.com/llnl/conduit.git . && \
    git checkout tags/v0.9.2 && \
    mkdir build && cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=$CONDUIT_PREFIX ../src/ -DCMAKE_BUILD_TYPE=Release -DENABLE_MPI=ON && \
    make -j2 && \
    make install
```

### Conan Installation

Godrick relies on Conan to install another set of dependencies which are not provided by packages.
Here is how to install and setup Conan:
```
pip3 install -q --no-cache-dir conan==1.62.0 conan-package-tools
mkdir -p $HOME/.conan
```

### Godrick Installation 

Now that all the necessary dependencies are installed, we can install Godrick itself:
```
export CONDUIT_PREFIX=$HOME/.local
export GODRICK_SOURCE_DIR=$HOME/dev/godrick
export GODRICK_PREFIX=$HOME/.local

mkdir -p $GODRICK_SOURCE_DIR
cd $GODRICK_SOURCE_DIR
git clone --recursive https://github.com/madreher/Godrick.git . && \
    mkdir build && cd build && \
    ../run_cmake_script.sh && \
    make -j2 && \
    make install
pip3 install -e .
```

Note that Godrick is composed of a runtime and a Python library which have both to be installed.

## Godrick in Details

Godrick is composed of two phases: declaring a workflow (i.e the different taks and communication channels), and the runtime which is executing the workflow on a set of compute resources. In this section, we will cover both these aspects separatly. 

### Declaring a Workflow

#### Tasks

A `Task` object in Godrick represents an executable able to send and receive data from other `Task`. A `Task` is general described by a unique name, a command line, a set of compute resources, and a list of input and output ports. Input and output port are abstractions to receive and send data respectively on a individual communication channel. An individual `Task` can be a parallel application, either via multi-threading or multi-processing. Internally, a `Task` object can be represented as a list of processes, where each process has a list of compute resources assigned to it. Input and output ports are duplicated for each process part of the `Task`. The number of individual processes is definited by the type of `Task`, the amount of computational resources assign to the `Task`, and the placement policy of the `Task` on these resources. 

For example, let's consider a `SingleProcessTask`. This `Task` object is designed to host only one process, and will therefor only spawn one instance of each of its ports. 
However, this `Task` may still be assigned multiple cores which can be used by the executable of the task for multi-threading for instance.

TODO: Add python example, Do issue 22

Let's now consider an `MPITask`. An `MPITask` is the object to define a multi-process task. The number of processes created depends on the amount of compute resources assigned to the task, as well as the placement policy of the task on these resources.

```
from godrick.task import MPITask, MPIPlacementPolicy
from godrick.computeResources import ComputeCollection

# Create resources
# In this example, we load a dummy cluster composed of a single node name localhost with N cores
exampleFile = os.path.join(Path(__file__).resolve().parent, "../../data/tests/localhost.txt")
cluster = ComputeCollection(name="myCluster")
cluster.initFromHostFile(exampleFile, True) # Enable HT for each core

# Extract two set of resources: a partition composed of 1 physical core, another composed of 3 cores
partitions = cluster.splitNodesByCoreRange([1, 3])

# Create a MPITask with a command line, an input port, a placement policy, and a set of resources
task = MPITask(name="receivePartial", cmdline="bin/receivePartial --name receivePartial --config config.MPIPartialBcastWorkflow.json", placementPolicy=MPIPlacementPolicy.ONETASKPERCORE)
task.addInputPort("in")
task.setResources(partitions[1])
```
This this example, we create a `MPITask` and assign a partition of 3 physical cores / 6 logical threads to the `Task` since hyperthreading is enabled. We also assign the policy `MPIPlacementPolicy.ONETASKPERCORE` to it. With this policy, one process will be created per phyisical core. In this example, since 3 cores are assigned to the `MPITask`, three individual processes will be created. This also means that each process will have an input port named `in`.

#### Communication Channels

TODO:
- Transport method
- Paired VS Gate channels
- Protocols

#### Workflow and Launcher

TODO: 
- Main launcher
- files produced
- Work in progress to support SSH launcher

### Runtime API

#### The handler 

TODO:
- descript the base handler object and how its initialized

#### Datamodel

TODO:
- Basic description of Conduit and how to create simple data objects


#### Input and Output Ports

TODO:
- How to receive and send data
- Different flags possible when receiving data
- Lifespan of the data being sent