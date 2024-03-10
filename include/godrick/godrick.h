#pragma once

#include <string>
#include <unordered_map>
#include <vector>

#include <godrick/port.h>

#include <conduit/conduit.hpp>

namespace godrick {

class Godrick
{

public:
    Godrick(){}
    virtual ~Godrick(){}
    virtual bool initFromJSON(const std::string& jsonPath, const std::string& taskName);

    virtual void close(){}

    std::vector<std::string> getInputPortList() const;
    std::vector<std::string> getOutputPortList() const;

    bool push(const std::string& portName, conduit::Node& data) const;
    bool get(const std::string& portName, std::vector<conduit::Node>& data) const;

protected:
    std::unordered_map<std::string, InputPort>  m_inputPorts;
    std::unordered_map<std::string, OutputPort> m_outputPorts;

}; // Godrick

} // godrick