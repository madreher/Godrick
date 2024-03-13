#pragma once 

#include <godrick/mpi/protocolImplMPI.h>

#include <mpi.h>

namespace godrick {

namespace mpi {

class BroadcastProtocolImplMPI : public ProtocolImplMPI
{
public:
    BroadcastProtocolImplMPI() : ProtocolImplMPI(){}
    BroadcastProtocolImplMPI(MPI_Comm comm, 
                    int localInStartRank,
                    int localInSize,
                    int localOutStartRank,
                    int localOutSize,
                    int localRank,
                    bool isSource) : ProtocolImplMPI(comm, localInStartRank, localInSize, localOutStartRank, localOutSize, localRank, isSource){}

    virtual ~BroadcastProtocolImplMPI(){}

    virtual bool isValid() const override;
    virtual bool send(conduit::Node& data) override;
    virtual bool receive(std::vector<conduit::Node>& data) override;
    virtual void print() override;
};

} // mpi

} // godrick