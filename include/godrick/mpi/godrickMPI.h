#pragma once

#include <godrick/godrick.h>

#include <mpi.h>

namespace godrick {

namespace mpi {

class GodrickMPI : public Godrick
{
public:
    GodrickMPI() : Godrick(){}
    virtual ~GodrickMPI() override {}
    virtual bool initFromJSON(const std::string& jsonPath, const std::string& taskName) override;

    MPI_Comm getTaskCommunicator() const { return m_taskComm; }
    int getTaskRank() const { return m_taskRank; }

    virtual void close() override;

protected:
    bool initMPIInfo(int startRank, int nbRanks);

    int m_globalTaskStartRank = -1;
    int m_globalTaskCommSize = -1;

    MPI_Comm m_taskComm = MPI_COMM_NULL;
    int m_taskRank = -1;
};

} // mpi

} // godrick