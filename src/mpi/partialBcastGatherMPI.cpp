#include <godrick/mpi/partialBcastGatherMPI.h>

godrick::mpi::PartialBCastGatherProtocolImplMPI::PartialBCastGatherProtocolImplMPI(MPI_Comm comm, 
                    int localInStartRank,
                    int localInSize,
                    int localOutStartRank,
                    int localOutSize,
                    int localRank,
                    bool isSource) : ProtocolImplMPI(comm, localInStartRank, localInSize, localOutStartRank, localOutSize, localRank, isSource)
{
    m_isBroadcast = (m_localOutSize < m_localInSize);
}

bool godrick::mpi::PartialBCastGatherProtocolImplMPI::isValid() const
{
    // Check for a fixed ratio between producer in consumer. This is to avoid having to have 
    // a consumer or producer sending or receiving one more messages than the other.
    // This limitation may be removed at some point if necessary
    if(m_isBroadcast)
        return m_localInSize % m_localOutSize == 0; // Check if the number of producer dvides the number of consumers
    else
        return m_localOutSize % m_localInSize == 0; // Check if the number of consumers dvides the number of producer
}

bool godrick::mpi::PartialBCastGatherProtocolImplMPI::send(conduit::Node& data) const
{
    (void)data;
    return false;
}
bool godrick::mpi::PartialBCastGatherProtocolImplMPI::receive(std::vector<conduit::Node>& data) const
{
    (void)data;
    return false;
}