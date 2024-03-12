#pragma once 

#include <godrick/mpi/protocolImplMPI.h>

#include <mpi.h>

namespace godrick {

namespace mpi {

class PartialBCastGatherProtocolImplMPI : public ProtocolImplMPI
{
public:
    PartialBCastGatherProtocolImplMPI() : ProtocolImplMPI(){}
    PartialBCastGatherProtocolImplMPI(MPI_Comm comm, 
                    int localInStartRank,
                    int localInSize,
                    int localOutStartRank,
                    int localOutSize,
                    int localRank) : ProtocolImplMPI(comm, localInStartRank, localInSize, localOutStartRank, localOutSize, localRank){}

    virtual ~PartialBCastGatherProtocolImplMPI(){}

    virtual bool send(conduit::Node& data) const override;
    virtual bool receive(std::vector<conduit::Node>& data) const override;
};

} // mpi

} // godrick