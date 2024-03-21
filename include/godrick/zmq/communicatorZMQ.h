#pragma once

#include <godrick/communicator.h>

#include <zmq.hpp>

namespace godrick {

namespace grzmq {

class CommunicatorZMQ : public Communicator 
{
public:
    CommunicatorZMQ() : Communicator(), m_context(1) {}
    virtual ~CommunicatorZMQ(){}

    virtual bool initFromJSON(json& data) override;

    virtual bool send(conduit::Node& data) override;
    virtual bool receive(std::vector<conduit::Node>& data) override;
    virtual void flush() override {}

protected:
    zmq::context_t m_context;
};

} // zmq

} // godrick