#pragma once

#include <string>
#include <vector>
#include <unordered_map>

#include <conduit/conduit.hpp>

#include <nlohmann/json.hpp>
using json = nlohmann::json;

namespace godrick {

enum class MessageResponse : uint8_t
{
    TOKEN = 0,      // System message type generated to unlock loops
    TERMINATE = 1,  // System message type generated when calling close()
    MESSAGES = 2,   // Regular messages
    EMPTY = 3,      // Try to receive messages but nothing is available. Only used by gates
    ERROR = 4
};

class Communicator
{
public:
    Communicator(){}
    virtual ~Communicator() = default;

    std::string getName() const { return m_name; }
    void setName(const std::string name){ m_name = name; } 

    int32_t getNbTokenLeft() const { return m_nbTokenLeft; }
    void setNbTokenLeft(int32_t nbToken) { m_nbTokenLeft = nbToken; }

    virtual bool initFromJSON(json& data, const std::string& taskName);

    virtual bool send(conduit::Node& data) = 0;
    virtual MessageResponse receive(std::vector<conduit::Node>& data) = 0;
    virtual void flush(){}

protected:
    std::string m_name;
    int32_t m_nbTokenLeft = 0;
}; // Communicator

} // godrick