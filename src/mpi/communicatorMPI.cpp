#include <godrick/mpi/communicatorMPI.h>

#include <spdlog/spdlog.h>

bool godrick::mpi::CommunicatorMPI::initFromJSON(json& data)
{
    if(data.count("type") == 0 || data.at("type").get<std::string>().compare("MPI") != 0)
    {
        spdlog::error("Wrong communicator type associated with the communicator. This reader can only process MPI commuinicator.");
        return false;
    }

    // Get the global ranking information
    m_globalInStartRank     = data.at("inStartRank").get<int>();        // Rank of the INPUT PORT = destination
    m_globalInSize          = data.at("inSize").get<int>();
    m_globalOutStartRank    = data.at("outStartRank").get<int>();       // Rank of the OUTPUT PORT = source
    m_globalOutSize         = data.at("outSize").get<int>();

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

    return true;
}