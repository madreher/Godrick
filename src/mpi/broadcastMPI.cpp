#include <godrick/mpi/broadcastMPI.h>

#include <conduit/conduit_relay_mpi.hpp>

bool godrick::mpi::BroadcastProtocolImplMPI::send(conduit::Node& data) const
{
    conduit::relay::mpi::broadcast_using_schema(data, m_localOutStartRank, m_localComm);
    return true;
}
bool godrick::mpi::BroadcastProtocolImplMPI::receive(std::vector<conduit::Node>& data) const
{
    data.resize(1);
    conduit::relay::mpi::broadcast_using_schema(data[0], m_localOutStartRank, m_localComm);
    return true;
}