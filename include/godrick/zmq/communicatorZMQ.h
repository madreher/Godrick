#pragma once

#include <godrick/communicator.h>

#include <zmq.hpp>

namespace godrick {

namespace grzmq {

enum class ZMQCommProtocol : uint8_t
{
    PUSH_PULL = 0,
    PUB_SUB = 1
};

static std::unordered_map<std::string, ZMQCommProtocol> strToZMQCommProtocol = {
    {"PUSH_PULL", ZMQCommProtocol::PUSH_PULL},
    {"PUB_SUB", ZMQCommProtocol::PUB_SUB}
};


class CommunicatorZMQ : public Communicator 
{
public:
    CommunicatorZMQ() : Communicator(), m_context(1) {}
    ~CommunicatorZMQ() = default;

    virtual bool initFromJSON(json& data, const std::string& taskName) override;

    virtual bool send(conduit::Node& data) override;
    virtual MessageResponse receive(std::vector<conduit::Node>& data) override;
    virtual void flush() override {}

protected:
    zmq::context_t m_context;
    ZMQCommProtocol m_protocol = ZMQCommProtocol::PUB_SUB;
    zmq::socket_t m_socket;
};

} // zmq

} // godrick