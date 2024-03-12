#pragma once

#include <string>
#include <vector>
#include <unordered_map>

#include <conduit/conduit.hpp>

#include <nlohmann/json.hpp>
using json = nlohmann::json;

namespace godrick {

enum class MPICommProtocol : uint8_t
{
    BROADCAST = 0,
    PARTIAL_BCAST_GATHER = 1
};

static std::unordered_map<std::string, MPICommProtocol> strToMPICommProtocol = {
    {"BROADCAST", MPICommProtocol::BROADCAST},
    {"PARTIAL_BCAST_GATHER", MPICommProtocol::PARTIAL_BCAST_GATHER}
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
    MPICommProtocol m_protocol = MPICommProtocol::BROADCAST;
}; // Communicator

} // godrick