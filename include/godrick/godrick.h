#pragma once

#include <string>
#include <unordered_map>
#include <vector>

#include <godrick/port.h>

#include <conduit/conduit.hpp>

namespace godrick {

enum class MessageResponse : uint8_t
{
    TOKEN = 0,      // System message type generated to unlock loops
    TERMINATE = 1,  // System message type generated when calling close()
    MESSAGES = 2,   // Regular messages
    EMPTY = 3,      // Try to receive messages but nothing is available. Only used by gates
    ERROR = 4
};

class Godrick
{

public:
    Godrick(){}
    virtual ~Godrick(){}
    virtual bool initFromJSON(const std::string& jsonPath, const std::string& taskName);

    virtual void close();

    std::vector<std::string> getInputPortList() const;
    std::vector<std::string> getOutputPortList() const;

    bool push(const std::string& portName, conduit::Node& data, bool autoFlush = false) const;
    void flush(const std::string& portName);
    MessageResponse get(const std::string& portName, std::vector<conduit::Node>& data);


protected:
    std::unordered_map<std::string, InputPort>  m_inputPorts;
    std::unordered_map<std::string, OutputPort> m_outputPorts;

}; // Godrick

} // godrick