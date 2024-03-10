#pragma once

#include <string>
#include <vector>

#include <conduit/conduit.hpp>

#include <nlohmann/json.hpp>
using json = nlohmann::json;

namespace godrick {

enum class CommProtocol : uint8_t
{
    BROADCAST = 0
};

class Communicator
{
public:
    Communicator(){}
    virtual ~Communicator(){}

    virtual bool initFromJSON(json& data);

    virtual bool send(conduit::Node& data) const = 0;
    virtual bool receive(std::vector<conduit::Node>& data) const = 0;

protected:
    std::string m_name;
    CommProtocol m_protocol = CommProtocol::BROADCAST;
}; // Communicator

} // godrick