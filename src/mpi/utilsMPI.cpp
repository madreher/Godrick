#include <godrick/mpi/utilsMPI.h>

MPI_Comm godrick::mpi::utils::collectiveCreateSubCommunicator(MPI_Comm baseComm, int startRank, int endRank)
{
    MPI_Comm newComm;
    MPI_Group group, newgroup;
    int range[3];
    range[0] = startRank;
    range[1] = endRank;
    range[2] = 1;
    MPI_Comm_group(baseComm, &group);
    MPI_Group_range_incl(group, 1, &range, &newgroup);
    MPI_Comm_create_group(baseComm, newgroup, 0, &newComm);
    MPI_Group_free(&group);
    MPI_Group_free(&newgroup);

    return newComm;
}