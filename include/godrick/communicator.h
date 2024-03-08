#pragma once

#include <string>

#include <nlohmann/json.hpp>
using json = nlohmann::json;

namespace godrick {

class Communicator
{
public:
    Communicator(){}
    virtual ~Communicator(){}

    virtual bool initFromJSON(json& data);

protected:
    std::string m_name;
}; // Communicator

} // godrick