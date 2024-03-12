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
                    int localRank) : ProtocolImplMPI(comm, localInStartRank, localInSize, localOutStartRank, localOutSize, localRank){}

    virtual ~BroadcastProtocolImplMPI(){}

    virtual bool send(conduit::Node& data) const override;
    virtual bool receive(std::vector<conduit::Node>& data) const override;
};

} // mpi

} // godrick