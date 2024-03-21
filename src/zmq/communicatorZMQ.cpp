#include <godrick/zmq/communicatorZMQ.h>

bool godrick::grzmq::CommunicatorZMQ::initFromJSON(json& data)
{
    (void)data;
    return false;
}

bool godrick::grzmq::CommunicatorZMQ::send(conduit::Node& data)
{
    (void)data;
    return false;
}

bool godrick::grzmq::CommunicatorZMQ::receive(std::vector<conduit::Node>& data)
{
    (void)data;
    return false;
}