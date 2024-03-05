#pragma once

#include <godrick/godrick.h>

#include <mpi.h>

namespace godrick {

namespace mpi {

class GodrickMPI : public Godrick
{
public:
    GodrickMPI() : Godrick(){}
    virtual ~GodrickMPI() override {}
    virtual bool initFromJSON(const std::string& jsonPath) override;
protected:
    int rank = -1;
    int size = -1;
};

} // mpi

} // godrick