#pragma once

#include <godrick/communicator.h>
#include <godrick/mpi/protocolImplMPI.h>

#include <mpi.h>
#include <nlohmann/json.hpp>
using json = nlohmann::json;

namespace godrick {

namespace mpi {

enum class MPICommProtocol : uint8_t
{
    BROADCAST = 0,
    PARTIAL_BCAST_GATHER = 1
};

static std::unordered_map<std::string, MPICommProtocol> strToMPICommProtocol = {
    {"BROADCAST", MPICommProtocol::BROADCAST},
    {"PARTIAL_BCAST_GATHER", MPICommProtocol::PARTIAL_BCAST_GATHER}
};


class CommunicatorMPI : public Communicator
{
public:
    CommunicatorMPI() : Communicator(){}
    ~CommunicatorMPI() = default;

    virtual bool initFromJSON(json& data, const std::string& taskName) override;

    virtual bool send(conduit::Node& data) override;
    virtual bool receive(std::vector<conduit::Node>& data) override;
    virtual void flush() override;

protected:
    MPICommProtocol m_protocol = MPICommProtocol::BROADCAST;

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

    // Local process information
    int m_localRank = -1;
    bool m_isSource = false;    // TODO: can only be used if overlapping is not allowed. 
    std::unique_ptr<ProtocolImplMPI> m_protocolImpl;


}; // CommunicatorMPI

} // mpi

} // godrick