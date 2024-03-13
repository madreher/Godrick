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

/*bool godrick::mpi::PartialBCastGatherProtocolImplMPI::send(conduit::Node& data)
{
    MsgSentEntry entry;

    int dataSize = 0;   // int because of MPI
    int schemaSize = 0; // int because of MPI

    // Because we are doing asynchronous transfer, we have to do a copy of the data
    // into a buffer to avoid problems if the original nodes become out of scope 
    // during the transfer. This also ensures that the buffer is contiguous and 
    // can be sent as a single array for the data part.
    // Source: conduit_relay_mpi.cpp in conduit repo

    conduit::Node &dataNodeCompact = entry.data["data"];
    data.compact_to(dataNodeCompact);
    
    entry.data["schema"] =  dataNodeCompact.schema().to_json();
    schemaSize = static_cast<int>(entry.data["schema"].dtype().number_of_elements());
    dataSize = static_cast<int>(entry.data.total_bytes_compact());
    spdlog::info("Sender prepare {} bytes for schema, and {} for data.", schemaSize, dataSize);

    // First sending the schema to all the receivers
    for(auto & dest : m_destinations)
    {
        entry.requests.emplace_back();
        MPI_Isend(  entry.data["schema"].data_ptr(),
                    schemaSize,
                    MPI_CHAR,
                    dest,
                    m_sentMsgID,
                    m_localComm,
                    &entry.requests.back());
        spdlog::info("Sending schema from {} to {}.", m_localRank, dest);
    }
    m_sentMsgID = (m_sentMsgID == INT_MAX ? 0 : m_sentMsgID + 1);

    // Then sending the data buffer
    for(auto & dest : m_destinations)
    {
        entry.requests.emplace_back();
        MPI_Isend(  dataNodeCompact.data_ptr(),
                    dataSize,
                    MPI_BYTE,
                    dest,
                    m_sentMsgID,
                    m_localComm,
                    &entry.requests.back());
    }
    m_sentMsgID = (m_sentMsgID == INT_MAX ? 0 : m_sentMsgID + 1);

    // Add done, we can push the entry
    m_transitMessages.push_back(std::move(entry));

    return true;
}*/

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
    
    conduit::Node n_msg(s_msg_compact);
    // these sets won't realloc since schemas are compatible
    n_msg["schema_len"].set(static_cast<int64_t>(snd_schema_json.length()));
    n_msg["schema"].set(snd_schema_json);
    n_msg["data"].update(data);

    
    size_t msg_data_size = static_cast<size_t>(n_msg.total_bytes_compact());
    
    if(!conduit::utils::value_fits<size_t,int>(msg_data_size))
    {
        spdlog::warn("Warning size value ( {} ) exceeds the size of MPI_Send max value ( {} )", msg_data_size, std::numeric_limits<int>::max());
    }

    // Sending the data to all the destinations
    MsgSentEntry entry;
    for(auto & dest : m_destinations)
    {
        entry.requests.emplace_back();
        MPI_Isend(  n_msg.data_ptr(),
                    static_cast<int>(msg_data_size),
                    MPI_BYTE,
                    dest,
                    m_sentMsgID,
                    m_localComm,
                    &entry.requests.back());
        spdlog::info("Sending schema from {} to {}.", m_localRank, dest);
    }
    m_sentMsgID = (m_sentMsgID == INT_MAX ? 0 : m_sentMsgID + 1);

    return true;
}

bool godrick::mpi::PartialBCastGatherProtocolImplMPI::receive(std::vector<conduit::Node>& data)
{
    // code taken from recv_using_schema in conduit_relay_mpi.cpp

    // Prepare the data 
    data.resize(static_cast<size_t>(m_nbExpectedReception));
    spdlog::info("Rank {} preparing to receive {} schemas.", m_localRank, m_nbExpectedReception);
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
        gen.walk(rcv_schema);

        // advance by the schema length
        n_buff_ptr += n_msg["schema"].total_bytes_compact();
        
        // apply the schema to the data
        n_msg["data"].set_external(rcv_schema,n_buff_ptr);
        
        // copy out to our result node
        data[sourceIndex].update(n_msg["data"]);
    }

    return true;
}

/*bool godrick::mpi::PartialBCastGatherProtocolImplMPI::receive(std::vector<conduit::Node>& data)
{
    // Prepare the data 
    data.resize(static_cast<size_t>(m_nbExpectedReception));
    spdlog::info("Rank {} preparing to receive {} schemas.", m_localRank, m_nbExpectedReception);

    // First, we are going to receive the schemas
    for(int i = 0; i < m_nbExpectedReception; ++i)
    {
        MPI_Status status;
        MPI_Probe(MPI_ANY_SOURCE, m_expectedMsgID, m_localComm, &status);
        
        // Check from which source the schema came from
        size_t sourceIndex = static_cast<size_t>(status.MPI_SOURCE - m_firstRankSource);

        // Allocate the schema buffer accordingly
        int nbytes;                           
        MPI_Get_count(&status, MPI_BYTE, &nbytes);
        data[sourceIndex]["schema"].set(conduit::DataType::char8_str(nbytes));

        // Buffer has been allocated, now we can receive the data
        MPI_Recv(   data[sourceIndex]["schema"].data_ptr(), 
                    nbytes, 
                    MPI_CHAR, 
                    status.MPI_SOURCE,
                    m_expectedMsgID, 
                    m_localComm, 
                    &status);

        // Setting the schema
        conduit::Schema bcast_schema;
        conduit::Generator gen(data[sourceIndex]["schema"].as_char8_str());
        gen.walk(bcast_schema);
        data[sourceIndex].set_schema(bcast_schema); // At this point, the Node has a memory layout properly sized for message reception
        spdlog::info("Rank {} has received a schema from {} ({} allocated).", m_localRank, status.MPI_SOURCE, nbytes);
    }
    m_expectedMsgID = (m_expectedMsgID == INT_MAX ? 0 : m_expectedMsgID + 1);

    // Then we can receive the actual data
    // First, we are going to receive the schemas
    for(int i = 0; i < m_nbExpectedReception; ++i)
    {
        MPI_Status status;
        MPI_Probe(MPI_ANY_SOURCE, m_expectedMsgID, m_localComm, &status);
        
        // Check from which source the schema came from
        size_t sourceIndex = static_cast<size_t>(status.MPI_SOURCE - m_firstRankSource);

        // Allocate the schema buffer accordingly
        int nbytes;                           
        MPI_Get_count(&status, MPI_BYTE, &nbytes);

        // Buffer has been allocated, now we can receive the data
        MPI_Recv(   data[sourceIndex].data_ptr(), 
                    nbytes,     // Should match data[sourceIndex].total_bytes_compact()
                    MPI_BYTE, 
                    status.MPI_SOURCE,
                    m_expectedMsgID, 
                    m_localComm, 
                    &status);
        spdlog::info("Rank {} has received a data ({}) from {} ({} in the node allocated).", m_localRank, nbytes, status.MPI_SOURCE, data[sourceIndex].total_bytes_compact());
    }
    m_expectedMsgID = (m_expectedMsgID == INT_MAX ? 0 : m_expectedMsgID + 1);

    return true;
}
*/

/*void
decaf::
RedistProcMPI::redistribute(pConstructData &data, RedistRole role)
{
    if (role == DECAF_REDIST_SOURCE)
    {
        for (int i = 0; i < nbSends_; i++)
        {
            if (rank_ == local_dest_rank_ + destination_ + i)
            {
                transit = data;
            }
            else
            {
                //MPI_Request req;
                //reqsPayload.push_back(req);
                reqsPayload.emplace_back(MPI_Request());
                reqsKeys.push_back(idMsg);
                msgsString[idMsg] = std::string();
                //msgsString[idMsg].resize(data->getOutSerialBufferSize());
                //memcpy(&(msgsString[idMsg][0]), data->getOutSerialBuffer(), data->getOutSerialBufferSize());
                data->serialize(msgsString.at(idMsg));
                MPI_Isend(&(msgsString[idMsg][0]),
                          //data->getOutSerialBufferSize(),
                          static_cast<int>(msgsString[idMsg].size()),
                          MPI_BYTE,  local_dest_rank_ + destination_ + i,
                          send_data_tag, communicator_,&reqsPayload.back());
                idMsg++;
            }
        }
        send_data_tag = (send_data_tag == INT_MAX ? MPI_DATA_TAG : send_data_tag + 1);
    }

    // check if we have something in transit to/from self
    if (role == DECAF_REDIST_DEST && !transit.empty())
    {
        if (mergeMethod_ == DECAF_REDIST_MERGE_STEP)
            data->merge(transit->getOutSerialBuffer(), transit->getOutSerialBufferSize());
        else if (mergeMethod_ == DECAF_REDIST_MERGE_ONCE)
            data->unserializeAndStore(transit->getOutSerialBuffer(),
                                      transit->getOutSerialBufferSize());
        transit.reset();              // we don't need it anymore, clean for the next iteration
        if (nbSources_ > nbDests_)
            nbReceptions_ = nbSources_ / nbDests_ - 1;
        else
            nbReceptions_ = 0;        // Broadcast case : we got the only data we will receive
    }

    // only consumer ranks are left
    if (role == DECAF_REDIST_DEST)
    {
        for (int i = 0; i < nbReceptions_; i++)
        {
            MPI_Status status;
            MPI_Probe(MPI_ANY_SOURCE, recv_data_tag, communicator_, &status);
            int nbytes;                           // number of bytes in the message
            MPI_Get_count(&status, MPI_BYTE, &nbytes);
            data->allocate_serial_buffer(static_cast<size_t>(nbytes)); // allocate necessary space
            MPI_Recv(data->getInSerialBuffer(), nbytes, MPI_BYTE, status.MPI_SOURCE,
                     recv_data_tag, communicator_, &status);


            if (mergeMethod_ == DECAF_REDIST_MERGE_STEP)
                data->merge();
            else if (mergeMethod_ == DECAF_REDIST_MERGE_ONCE)
                //data->unserializeAndStore();
                data->unserializeAndStore(data->getInSerialBuffer(), static_cast<size_t>(nbytes));
            else
            {
                fprintf(stderr, "ERROR: merge method not specified. Aborting.\n");
                MPI_Abort(MPI_COMM_WORLD, 0);
            }
        }
        recv_data_tag = (recv_data_tag == INT_MAX ? MPI_DATA_TAG : recv_data_tag + 1);

        if (mergeMethod_ == DECAF_REDIST_MERGE_ONCE)
            data->mergeStoredData();
    }
}*/

/*
int
broadcast_using_schema(Node &node,
                       int root,
                       MPI_Comm comm)
{
    int rank = mpi::rank(comm);

    Node bcast_buffers;

    void *bcast_data_ptr = NULL;
    int   bcast_data_size = 0;

    int bcast_schema_size = 0;
    int rcv_bcast_schema_size = 0;

    // setup buffers for send
    if(rank == root)
    {
        
        bcast_data_ptr  = node.contiguous_data_ptr();
        bcast_data_size = static_cast<int>(node.total_bytes_compact());
        
        if(bcast_data_ptr != NULL &&
           node.is_compact() && 
           node.is_contiguous())
        {
            bcast_buffers["schema"] = node.schema().to_json();
        }
        else
        {
            Node &bcast_data_compact = bcast_buffers["data"];
            node.compact_to(bcast_data_compact);
            
            bcast_data_ptr  = bcast_data_compact.data_ptr();
            bcast_buffers["schema"] =  bcast_data_compact.schema().to_json();
        }
     

        
        bcast_schema_size = static_cast<int>(bcast_buffers["schema"].dtype().number_of_elements());
    }

    int mpi_error = MPI_Allreduce(&bcast_schema_size,
                                  &rcv_bcast_schema_size,
                                  1,
                                  MPI_INT,
                                  MPI_MAX,
                                  comm);

    CONDUIT_CHECK_MPI_ERROR(mpi_error);

    bcast_schema_size = rcv_bcast_schema_size;

    // alloc for rcv for schema
    if(rank != root)
    {
        bcast_buffers["schema"].set(DataType::char8_str(bcast_schema_size));
    }

    // broadcast the schema 
    mpi_error = MPI_Bcast(bcast_buffers["schema"].data_ptr(),
                          bcast_schema_size,
                          MPI_CHAR,
                          root,
                          comm);

    CONDUIT_CHECK_MPI_ERROR(mpi_error);
    
    bool cpy_out = false;
    
    // setup buffers for receive 
    if(rank != root)
    {
        Schema bcast_schema;
        Generator gen(bcast_buffers["schema"].as_char8_str());
        gen.walk(bcast_schema);
        
        // only check compat for leaves
        // there are more zero copy cases possible here, but
        // we need a better way to identify them
        // compatible won't work for object cases that
        // have different named leaves
        if( !(node.dtype().is_empty() ||
              node.dtype().is_object() ||
              node.dtype().is_list() ) && 
            !(bcast_schema.dtype().is_empty() ||
              bcast_schema.dtype().is_object() ||
              bcast_schema.dtype().is_list() )
            // make sure `node` can hold data described by `bcast_schema`
            && node.schema().compatible(bcast_schema))
        {
            
            bcast_data_ptr  = node.contiguous_data_ptr();
            bcast_data_size = static_cast<int>(node.total_bytes_compact());
            
            if( bcast_data_ptr == NULL ||
                ! node.is_compact() )
            {
                Node &bcast_data_buffer = bcast_buffers["data"];
                bcast_data_buffer.set_schema(bcast_schema);
                
                bcast_data_ptr  = bcast_data_buffer.data_ptr();
                cpy_out = true;
            }
        }
        else
        {
            node.set_schema(bcast_schema);

            bcast_data_ptr  = node.data_ptr();
            bcast_data_size = static_cast<int>(node.total_bytes_compact());
        }
    }
    
    mpi_error = MPI_Bcast(bcast_data_ptr,
                          bcast_data_size,
                          MPI_BYTE,
                          root,
                          comm);

    CONDUIT_CHECK_MPI_ERROR(mpi_error);

    // note: cpy_out will always be false when rank == root
    if( cpy_out )
    {
        node.update(bcast_buffers["data"]);
    }

    return mpi_error;
}*/