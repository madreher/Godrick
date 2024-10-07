# Godrick

[![Godrick CI/CD](https://github.com/madreher/Godrick/actions/workflows/ci.yml/badge.svg)](https://github.com/madreher/Godrick/actions/workflows/ci.yml)
[![Coverage badge](https://raw.githubusercontent.com/madreher/Godrick/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/madreher/Godrick/blob/python-coverage-comment-action-data/htmlcov/index.html)
[![CPP Coverage Status](https://coveralls.io/repos/github/madreher/Godrick/badge.svg?branch=main)](https://coveralls.io/github/madreher/Godrick?branch=main)

## TLDR

Godrick is an in-situ middlware aiming at coupling HPC simulation codes with analysis and services, whether it be on the same compute environement or on remote resources connecting to the flow of data.

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
```

## Documentation

TODO
