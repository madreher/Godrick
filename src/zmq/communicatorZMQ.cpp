#include <godrick/zmq/communicatorZMQ.h>

#include <spdlog/spdlog.h>

bool godrick::grzmq::CommunicatorZMQ::initFromJSON(json& data, const std::string& taskName)
{
    if(data.count("type") == 0 || data.at("type").get<std::string>().compare("ZMQ") != 0)
    {
        spdlog::error("Wrong communicator type associated with the communicator. This reader can only process ZMQ commuinicator.");
        return false;
    }

    // First initialize from the parent class 
    if(!godrick::Communicator::initFromJSON(data, taskName))
        return false;

    spdlog::info("Loading the settings for the communicator {} from the task {}.", m_name, taskName);
    // Get socket information and protocol 
    m_protocol = strToZMQCommProtocol.at(data.at("zmqprotocol").get<std::string>());
    std::string receiverTask = data.at("inputTaskName").get<std::string>();
    std::string senderTask = data.at("outputTaskName").get<std::string>();

    bool isReceiver = receiverTask.compare(taskName) == 0;
    bool isSender = senderTask.compare(taskName) == 0;

    if(!isReceiver && !isSender)
    {
        spdlog::error("Trying to process the the communicator {} from task {}, but the task is neither the sender not the receiver. Something went wrong when processing the configuration file.", m_name, taskName);
        return false;
    }

    switch(m_protocol)
    {
        case ZMQCommProtocol::PUB_SUB:
        {
            std::string addr = data["protocolSettings"].at("pubaddr").get<std::string>();
            int port = data["protocolSettings"].at("pubport").get<int>();
            std::stringstream ss;
            ss<<"tcp://"<<addr<<":"<<port;
            if(isReceiver)
            {
                m_socket = zmq::socket_t(m_context, ZMQ_SUB);
                m_socket.connect(ss.str());
                m_socket.set(zmq::sockopt::subscribe, "");  // We subscribe to anything
                spdlog::info("Connecting the receiver {} to the address {}.", taskName, ss.str());
            }
            else
            {
                m_socket = zmq::socket_t(m_context, ZMQ_PUB);
                m_socket.bind(ss.str());
                spdlog::info("Binding the sender {} to the address {}.", taskName, ss.str());
            }
            return true;
        }
        case ZMQCommProtocol::PUSH_PULL:
        {
            std::string addr = data["protocolSettings"].at("pushaddr").get<std::string>();
            int port = data["protocolSettings"].at("pushport").get<int>();
            std::stringstream ss;
            ss<<"tcp://"<<addr<<":"<<port;
            if(isReceiver)
            {
                m_socket = zmq::socket_t(m_context, ZMQ_PULL);
                m_socket.connect(ss.str());
            }
            else
            {
                m_socket = zmq::socket_t(m_context, ZMQ_PUSH);
                m_socket.bind(ss.str());
            }
            return true;
        }
        default:
        {
            spdlog::error("Unable to process the ZMQ communication protocol {}. Either the type is unknown or not implemented yet.", data.at("zmqprotocol"));
            return false;
        }
    }

    return false;
}

bool godrick::grzmq::CommunicatorZMQ::send(conduit::Node& data)
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

    conduit::Node entry(s_msg_compact);
    // these sets won't realloc since schemas are compatible
    entry["schema_len"].set(static_cast<int64_t>(snd_schema_json.length()));
    entry["schema"].set(snd_schema_json);
    entry["data"].update(data);

    size_t msg_data_size = static_cast<size_t>(entry.total_bytes_compact());
    
    //if(!conduit::utils::value_fits<size_t,int>(msg_data_size))
    //{
    //    spdlog::warn("Warning size value ( {} ) exceeds the size of MPI_Send max value ( {} )", msg_data_size, std::numeric_limits<int>::max());
    //}
    //zmq::message_t msg(entry.data_ptr(), static_cast<int>(msg_data_size));
    zmq::message_t msg(entry.data_ptr(), msg_data_size);
    m_socket.send(msg, zmq::send_flags::none); // Not doing asynchronous for now.
    return true;
}

bool godrick::grzmq::CommunicatorZMQ::receive(std::vector<conduit::Node>& data)
{

    zmq::message_t msg;
    zmq::recv_result_t result = m_socket.recv(msg, zmq::recv_flags::none);
    if(!result.has_value())
    {
        spdlog::warn("The communicator {} didn't receive a message.", m_name);
        return false;
    }

    if(result.value() == 0)
    {
        spdlog::warn("Empty message received by the communicator {}.", m_name);
        return false;
    }

    data.resize(1);

    conduit::Node n_buffer(conduit::DataType::uint8(static_cast<int>(msg.size())));

    uint8_t *n_buff_ptr = reinterpret_cast<uint8_t*>(n_buffer.data_ptr());

    conduit::Node n_msg;

    // Copy the data to the conduit
    memcpy(n_buffer.data_ptr(), msg.data(), msg.size());

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
    data[0].update(n_msg["data"]);


    return true;
}