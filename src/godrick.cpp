#include <godrick/godrick.h>

#include <algorithm>

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