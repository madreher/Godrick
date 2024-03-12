#include <godrick/mpi/partialBcastGatherMPI.h>

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