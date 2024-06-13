#include <godrick/mpi/partialBcastGatherMPI.h>

#include <spdlog/spdlog.h>

godrick::mpi::PartialBCastGatherProtocolImplMPI::PartialBCastGatherProtocolImplMPI(MPI_Comm comm, 
                    int localInStartRank,
                    int localInSize,
                    int localOutStartRank,
                    int localOutSize,
                    int localRank,
                    bool isSource) : ProtocolImplMPI(comm, localInStartRank, localInSize, localOutStartRank, localOutSize, localRank, isSource)
{
    m_isBroadcast = (m_localOutSize < m_localInSize);

    //  IMPORTANT ASSUMPTION:   The number of sources divide the number of receivers (gather) OR
    //                          The number of receivers divide the number of sources (broadcast)

    // Setup additional variables for the sender side 
    if(localRank >= localOutStartRank && localRank < localOutStartRank + localOutSize)
    {
        int localSourceIndex = localRank - localOutStartRank;
        if(m_isBroadcast)
        {
            int receiversPerSource = localInSize / localOutSize; // A source will send a message to <reciverPerSource> receivers
            for(int i = 0; i < receiversPerSource; ++i)
                m_destinations.push_back(localInStartRank + localSourceIndex * receiversPerSource + i);
        }
        else
        {
            int sourcesPerReceiver = localOutSize / localInSize;
            int indexReceiver = localSourceIndex / sourcesPerReceiver;
            m_destinations.push_back(m_localInStartRank + indexReceiver);
        }
    }

    // Setup additional variables for the receiver side
    if(localRank >= localInStartRank && localRank < localInStartRank + localInSize)
    {
        int localReceiverIndex = localRank - localInStartRank;
        if(m_isBroadcast)
        {
            m_nbExpectedReception = 1;  // More source than receivers, a receiver will receive data from only 1 source
            int receiverPerSource = localInSize / localOutSize; // A source will send a message to <reciverPerSource> receivers
            m_firstRankSource = m_localOutStartRank + localReceiverIndex / receiverPerSource; // Calculate which source will send a message to this receiver

        }
        else 
        {   
            // More sources than receivers, the receiver will receive data from multiple sources
            m_nbExpectedReception = localOutSize / localInSize;
            m_firstRankSource = m_localOutStartRank + localReceiverIndex / m_nbExpectedReception;
        }
    }
    
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

void godrick::mpi::PartialBCastGatherProtocolImplMPI::flush()
{
    // For now, implementing a hard-blocking flush with MPI_Waitall()
    // Will have to add the option to use TestSome instead 

    // Waiting for the communication information to be receive
    for(auto & query : m_transitMessages)
    {
        if(query.requests.size())
        {
            MPI_Waitall(static_cast<int>(query.requests.size()), &query.requests[0], MPI_STATUS_IGNORE);
        }
    }
    m_transitMessages.clear();
}

bool godrick::mpi::PartialBCastGatherProtocolImplMPI::send(conduit::Node& data)
{
    conduit::Schema s_data_compact;
    
    // schema will only be valid if compact and contig
    if( data.is_compact() && data.is_contiguous())
    {
        s_data_compact = data.schema();
    }
    else
    {
        data.schema().compact_to(s_data_compact);
    }
    
    std::string snd_schema_json = s_data_compact.to_json();
        
    conduit::Schema s_msg;
    s_msg["schema_len"].set(conduit::DataType::int64());
    s_msg["schema"].set(conduit::DataType::char8_str(static_cast<int64_t>(snd_schema_json.size()+1)));
    s_msg["data"].set(s_data_compact);
    
    // create a compact schema to use
    conduit::Schema s_msg_compact;
    s_msg.compact_to(s_msg_compact);
    
    m_transitMessages.emplace_back(s_msg_compact);
    MsgSentEntry& entry = m_transitMessages.back();
    // these sets won't realloc since schemas are compatible
    entry.data["schema_len"].set(static_cast<int64_t>(snd_schema_json.length()));
    entry.data["schema"].set(snd_schema_json);
    entry.data["data"].update(data);

    
    size_t msg_data_size = static_cast<size_t>(entry.data.total_bytes_compact());
    
    if(!conduit::utils::value_fits<size_t,int>(msg_data_size))
    {
        spdlog::warn("Warning size value ( {} ) exceeds the size of MPI_Send max value ( {} )", msg_data_size, std::numeric_limits<int>::max());
    }

    // Sending the data to all the destinations
    for(auto & dest : m_destinations)
    {
        spdlog::trace("Sending schema from {} to {}: {}", m_localRank,dest, entry.data["schema"].as_char8_str());
        entry.requests.emplace_back();
        MPI_Isend(  entry.data.data_ptr(),
                    static_cast<int>(msg_data_size),
                    MPI_BYTE,
                    dest,
                    m_sentMsgID,
                    m_localComm,
                    &entry.requests.back());
    }
    m_sentMsgID = (m_sentMsgID == INT_MAX ? 0 : m_sentMsgID + 1);

    return true;
}

bool godrick::mpi::PartialBCastGatherProtocolImplMPI::receive(std::vector<conduit::Node>& data)
{
    // code taken from recv_using_schema in conduit_relay_mpi.cpp

    // Prepare the data 
    data.resize(static_cast<size_t>(m_nbExpectedReception));
    spdlog::trace("Rank {} preparing to receive {} node.", m_localRank, m_nbExpectedReception);
    for(int i = 0; i < m_nbExpectedReception; ++i)
    {
        MPI_Status status;
        
        MPI_Probe(MPI_ANY_SOURCE, m_expectedMsgID, m_localComm, &status);
        
        // Check from which source the schema came from
        size_t sourceIndex = static_cast<size_t>(status.MPI_SOURCE - m_firstRankSource);
        
        int buffer_size = 0;
        MPI_Get_count(&status, MPI_BYTE, &buffer_size);

        conduit::Node n_buffer(conduit::DataType::uint8(buffer_size));
        
        MPI_Recv(n_buffer.data_ptr(),
                            buffer_size,
                            MPI_BYTE,
                            status.MPI_SOURCE,
                            status.MPI_TAG,
                            m_localComm,
                            &status);

        uint8_t *n_buff_ptr = reinterpret_cast<uint8_t*>(n_buffer.data_ptr());

        conduit::Node n_msg;
        // length of the schema is sent as a 64-bit signed int
        // NOTE: we aren't using this value  ... 
        n_msg["schema_len"].set_external(reinterpret_cast<int64_t*>(n_buff_ptr));
        n_buff_ptr +=8;
        // wrap the schema string
        n_msg["schema"].set_external_char8_str(reinterpret_cast<char*>(n_buff_ptr));
        // create the schema
        conduit::Schema rcv_schema;
        conduit::Generator gen(n_msg["schema"].as_char8_str());
        spdlog::trace("Rank {} received schema from {}: {}", m_localRank, status.MPI_SOURCE, n_msg["schema"].as_char8_str());
        gen.walk(rcv_schema);

        // advance by the schema length
        n_buff_ptr += n_msg["schema"].total_bytes_compact();
        
        // apply the schema to the data
        n_msg["data"].set_external(rcv_schema,n_buff_ptr);
        
        // copy out to our result node
        data[sourceIndex].update(n_msg["data"]);
    }

    m_expectedMsgID = (m_expectedMsgID == INT_MAX ? 0 : m_expectedMsgID + 1);

    return true;
}

