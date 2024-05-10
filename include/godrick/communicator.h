#pragma once

#include <string>
#include <vector>
#include <unordered_map>

#include <conduit/conduit.hpp>

#include <nlohmann/json.hpp>
using json = nlohmann::json;

namespace godrick {

class Communicator
{
public:
    Communicator(){}
    virtual ~Communicator() = default;

    virtual bool initFromJSON(json& data, const std::string& taskName);

    virtual bool send(conduit::Node& data) = 0;
    virtual bool receive(std::vector<conduit::Node>& data) = 0;
    virtual void flush(){}

protected:
    std::string m_name;
}; // Communicator

} // godrick