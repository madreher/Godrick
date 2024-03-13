#pragma once

#include <mpi.h>
#include <conduit/conduit.hpp>

namespace godrick {

namespace mpi {

class ProtocolImplMPI
{
public:
    ProtocolImplMPI(){}
    ProtocolImplMPI(MPI_Comm comm, 
                    int localInStartRank,
                    int localInSize,
                    int localOutStartRank,
                    int localOutSize,
                    int localRank,
                    bool isSource) : 
                    m_localComm(comm),
                    m_localInStartRank(localInStartRank),
                    m_localInSize(localInSize),
                    m_localOutStartRank(localOutStartRank),
                    m_localOutSize(localOutSize),
                    m_localRank(localRank),
                    m_isSource(isSource){}
    virtual ~ProtocolImplMPI(){}

    virtual bool isValid() const = 0;

    virtual bool send(conduit::Node& data) = 0;
    virtual bool receive(std::vector<conduit::Node>& data) = 0;
    virtual void flush(){}
    virtual void print(){}
protected:
    MPI_Comm m_localComm = MPI_COMM_NULL;
    int m_localInStartRank = -1;
    int m_localInSize = -1;
    int m_localOutStartRank = -1;
    int m_localOutSize = -1;

    // Local information
    int m_localRank = -1;
    bool m_isSource = false;
};

} // mpi

} // godrick