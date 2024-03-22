#include <godrick/mpi/communicatorMPI.h>
#include <godrick/mpi/broadcastMPI.h>
#include <godrick/mpi/partialBcastGatherMPI.h>

#include <spdlog/spdlog.h>

#include <conduit/conduit_relay_mpi.hpp>

bool godrick::mpi::CommunicatorMPI::initFromJSON(json& data, const std::string& taskName)
{
    if(data.count("type") == 0 || data.at("type").get<std::string>().compare("MPI") != 0)
    {
        spdlog::error("Wrong communicator type associated with the communicator. This reader can only process MPI commuinicator.");
        return false;
    }

    // First initialize from the parent class 
    if(!godrick::Communicator::initFromJSON(data, taskName))
        return false;

    // Get the global ranking information
    m_globalInStartRank     = data.at("inStartRank").get<int>();        // Rank of the INPUT PORT = destination
    m_globalInSize          = data.at("inSize").get<int>();
    m_globalOutStartRank    = data.at("outStartRank").get<int>();       // Rank of the OUTPUT PORT = source
    m_globalOutSize         = data.at("outSize").get<int>();

    m_localInSize = m_globalInSize;
    m_localOutSize = m_globalOutSize;

    // For now, we only support disjoints in and out ranks
    if(m_globalInStartRank < m_globalOutStartRank+m_globalOutSize && m_globalOutStartRank < m_globalInStartRank+m_globalInSize )
    {
        spdlog::error("Overlapping input and output ports are currently not supported by the CommunicatorMPI.");
        return false;
    }
    
    MPI_Comm commWorld = MPI_COMM_WORLD;

    // Create the MPI communicators for this
    MPI_Group group, groupRedist;
    MPI_Comm_group(commWorld, &group);

    // group covering both the sources and destinations
    // destination ranks need not be higher than source ranks

    int range_both[2][3];
    if(m_globalOutStartRank < m_globalInStartRank) //Separation to preserve the order of the ranks
    {
        range_both[0][0] = m_globalOutStartRank;
        range_both[0][1] = m_globalOutStartRank + m_globalInStartRank - 1;
        range_both[0][2] = 1;
        range_both[1][0] = m_globalInStartRank;
        range_both[1][1] = m_globalInStartRank + m_globalInSize - 1;
        range_both[1][2] = 1;
        m_localInStartRank = m_localOutSize;
        m_localOutStartRank = 0;
    }
    else
    {
        range_both[0][0] = m_globalInStartRank;
        range_both[0][1] = m_globalInStartRank + m_globalInSize - 1;
        range_both[0][2] = 1;
        range_both[1][0] = m_globalOutStartRank;
        range_both[1][1] = m_globalOutStartRank + m_globalOutSize - 1;
        range_both[1][2] = 1;
        m_localInStartRank = 0;
        m_localOutStartRank = m_globalInSize;

    }
    MPI_Group_range_incl(group, 2, range_both, &groupRedist);
    MPI_Comm_create_group(commWorld, groupRedist, 0, &m_localComm);
    MPI_Group_free(&groupRedist);

    // After this, we have a communicator which is composed of only the producer and the consumer
    MPI_Comm_rank(m_localComm, &m_localRank);
    if(m_localRank >= m_localOutStartRank && m_localRank < m_localOutStartRank+m_localOutSize)
        m_isSource = true;

    // Loading the communication protocol now that MPI is setup
    auto protocolName = data.at("mpiprotocol").get<std::string>();
    if(!strToMPICommProtocol.contains(protocolName))
    {
        spdlog::error("Unknown protocol {} received for the MPICommunicator. Choose a supported protocol.", protocolName);
        return false;
    }
    m_protocol = strToMPICommProtocol.at(protocolName);

    // Protocol processing 
    switch(m_protocol)
    {
        case MPICommProtocol::BROADCAST:
        {
            m_protocolImpl = std::make_unique<BroadcastProtocolImplMPI>(m_localComm, m_localInStartRank, m_localInSize, m_localOutStartRank, m_localOutSize, m_localRank, m_isSource);
            //m_protocolImpl->print();
            break;
        }
        case MPICommProtocol::PARTIAL_BCAST_GATHER:
        {
            m_protocolImpl = std::make_unique<PartialBCastGatherProtocolImplMPI>(m_localComm, m_localInStartRank, m_localInSize, m_localOutStartRank, m_localOutSize, m_localRank, m_isSource);
            break;
        }
        default:
        {
            spdlog::error("Protocol method {} not currently supported or implemented.", protocolName);
            return false;
        }
    }

    if(!m_protocolImpl->isValid())
    {
        spdlog::error("The communication protocol used by the communicator {} is not valid.", m_name);
        return false;
    }

    return true;
}

bool godrick::mpi::CommunicatorMPI::send(conduit::Node& data)
{
    if(!m_protocolImpl)
    {
        spdlog::error("The protocol implementation is not instanciated.");
        return false;
    }
    return m_protocolImpl->send(data);
}

bool godrick::mpi::CommunicatorMPI::receive(std::vector<conduit::Node>& data)
{
    if(!m_protocolImpl)
    {
        spdlog::error("The protocol implementation is not instanciated.");
        return false;
    }
    return m_protocolImpl->receive(data);
}

void godrick::mpi::CommunicatorMPI::flush()
{
    if(!m_protocolImpl)
    {
        spdlog::error("The protocol implementation is not instanciated.");
        return;
    }

    m_protocolImpl->flush();
}