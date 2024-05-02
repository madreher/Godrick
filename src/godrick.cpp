#include <godrick/godrick.h>
#include <godrick/messageUtils.h>

#include <algorithm>

#include <spdlog/spdlog.h>
#include <nlohmann/json.hpp>
using json = nlohmann::json;

bool godrick::Godrick::initFromJSON(const std::string& jsonPath, const std::string& taskName)
{
    (void)jsonPath;
    (void)taskName;
    return false;
}

auto keySelector = [](auto pair){ return pair.first; };

std::vector<std::string> godrick::Godrick::getInputPortList() const
{
    std::vector<std::string> keys(m_inputPorts.size());
    std::transform(m_inputPorts.begin(), m_inputPorts.end(), keys.begin(), keySelector);
    return keys;
}

std::vector<std::string> godrick::Godrick::getOutputPortList() const
{
    std::vector<std::string> keys(m_outputPorts.size());
    std::transform(m_outputPorts.begin(), m_outputPorts.end(), keys.begin(), keySelector);
    return keys;
}

bool godrick::Godrick::push(const std::string& portName, conduit::Node& data, bool autoFlush) const
{
    if(m_outputPorts.count(portName) == 0)
    {
        spdlog::error("Request to push on the output port {} but the port doesn't exist.", portName);
        return false;
    }
    else 
    {
        bool result =  m_outputPorts.at(portName).push(data);
        if(result && autoFlush)
        {
            m_outputPorts.at(portName).flush();
        }
        return result;
    }
}

void godrick::Godrick::flush(const std::string& portName)
{
    if(m_outputPorts.count(portName) == 0)
    {
        spdlog::error("Request to push on the output port {} but the port doesn't exist.", portName);
        return;
    }

    m_outputPorts.at(portName).flush();
}

bool godrick::Godrick::get(const std::string& portName, std::vector<conduit::Node>& data)
{
    if(m_inputPorts.count(portName) == 0)
    {
        spdlog::error("Request to get on the input port {} but the port doesn't exist.", portName);
        return false;
    }
    else
    { 
        bool result = m_inputPorts.at(portName).get(data);
        if(result)
        {
            for(auto & msg : data)
            {
                if(godrick::isTerminateMessage(msg))
                {
                    m_inputPorts.at(portName).setCloseFlag(true);
                    return false;
                }
            }
        }

        return true;
    }
}

void godrick::Godrick::close()
{
    conduit::Node msg;
    godrick::setTerminateMessage(msg);

    // Send the terminate message to all the receivers of this task
    for(auto & [k, v] : m_outputPorts)
    {
        spdlog::info("Pushing terminate to the port {}.", k);
        v.push(msg);
    }

    // Make sure that all the consumers have received the message
    for(auto & [k, v] : m_outputPorts)
    {
        spdlog::info("Flushing the port {}.", k);
        v.flush();
    }

    // For every input port, wait to receive a message if the port is not already closed.
    // This is to ensure that in case of cycle, all the components have received the close 
    // message before exiting the program.
    for(auto & [k, v] : m_inputPorts)
    {
        spdlog::info("Waiting for a message on port {}", k);
        std::vector<conduit::Node> tmp;
        if(!v.isClosed())
            v.get(tmp); 
    }
    spdlog::info("Close completed.");
}