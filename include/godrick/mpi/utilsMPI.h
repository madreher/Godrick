#pragma once

#include <mpi.h>

namespace godrick{

namespace mpi {

namespace utils 
{

MPI_Comm collectiveCreateSubCommunicator(MPI_Comm baseComm, int startRank, int endRank);

} // utils

} // mpi

} // godrick