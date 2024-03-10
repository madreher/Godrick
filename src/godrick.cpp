#include <godrick/godrick.h>

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

bool godrick::Godrick::push(const std::string& portName, conduit::Node& data) const
{
    if(m_outputPorts.count(portName) == 0)
    {
        spdlog::error("Request to push on the output port {} but the port doesn't exist.", portName);
        return false;
    }
    else 
        return m_outputPorts.at(portName).push(data);
}

bool godrick::Godrick::get(const std::string& portName, std::vector<conduit::Node>& data) const
{
    if(m_inputPorts.count(portName) == 0)
    {
        spdlog::error("Request to get on the input port {} but the port doesn't exist.", portName);
        return false;
    }
    else 
        return m_inputPorts.at(portName).get(data);
}