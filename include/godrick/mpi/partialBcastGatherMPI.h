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
                    int localRank,
                    bool isSource);

    virtual ~PartialBCastGatherProtocolImplMPI(){}

    virtual bool isValid() const override;
    virtual bool send(conduit::Node& data) const override;
    virtual bool receive(std::vector<conduit::Node>& data) const override;

protected:
    bool m_isBroadcast;
};

} // mpi

} // godrick