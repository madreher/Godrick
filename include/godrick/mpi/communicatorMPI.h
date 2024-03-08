#pragma once

#include <godrick/communicator.h>

#include <mpi.h>
#include <nlohmann/json.hpp>
using json = nlohmann::json;

namespace godrick {

namespace mpi {

class CommunicatorMPI : public Communicator
{
public:
    CommunicatorMPI() : Communicator(){}
    virtual ~CommunicatorMPI() override {}

    virtual bool initFromJSON(json& data) override;

protected:

    // Information of the input port (consumer) and output port (producer) in the 
    // global communicator, aka world comm
    int m_globalInStartRank  = -1;
    int m_globalInSize = -1;
    int m_globalOutStartRank = -1;
    int m_globalOutSize = -1;

    // Local communicator information including only the producer and consumer
    MPI_Comm m_localComm = MPI_COMM_NULL;
    int m_localInStartRank = -1;
    int m_localInSize = -1;
    int m_localOutStartRank = -1;
    int m_localOutSize = -1;

    // Local information
    int m_localRank = -1;
    bool m_isSource = false;
}; // CommunicatorMPI

} // mpi

} // godrick