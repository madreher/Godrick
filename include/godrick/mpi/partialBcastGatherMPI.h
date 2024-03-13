#pragma once 

#include <godrick/mpi/protocolImplMPI.h>

#include <mpi.h>

namespace godrick {

namespace mpi {

struct MsgSentEntry 
{
    conduit::Node data;
    std::vector<MPI_Request> requests;
};

class PartialBCastGatherProtocolImplMPI : public ProtocolImplMPI
{
public:
    PartialBCastGatherProtocolImplMPI() : ProtocolImplMPI(){}
    PartialBCastGatherProtocolImplMPI(MPI_Comm comm, 
                    int localInStartRank,
                    int localInSize,
                    int localOutStartRank,
                    int localOutSize,
                    int localRank,
                    bool isSource);

    virtual ~PartialBCastGatherProtocolImplMPI(){}

    virtual bool isValid() const override;
    virtual bool send(conduit::Node& data) override;
    virtual bool receive(std::vector<conduit::Node>& data) override;
    virtual void flush() override;

protected:
    bool m_isBroadcast;

    // Sender side info
    std::vector<int>            m_destinations;         // List of ranks to send 
    //std::vector<MPI_Request>    m_sentRequests;       // List of requests currently pending
    //std::vector<conduit::Node>  m_sentMessages;       // List of nodes current pending
    std::vector<MsgSentEntry>   m_transitMessages;
    int                         m_sentMsgID = 0;     // int because used for mpi tags

    // Receiver info
    int                         m_expectedMsgID = 0;     // Next expected message tag to wait for the schema
    int                         m_nbExpectedReception = 0;  // How many messages do we expect to receive
    int                         m_firstRankSource = 0;      // Rank of the first source. 1 source in case of broadcast, multiple when gather

};

} // mpi

} // godrick