#include <godrick/communicator.h>

#include <spdlog/spdlog.h>

bool godrick::Communicator::initFromJSON(json& data, const std::string& taskName)
{
    (void)taskName;
    if(!data.contains("name"))
    {
        spdlog::error("Unable to find the name of a communicator when loading.");
        return false;
    }

    m_name = data.at("name").get<std::string>(); 
    m_nbTokenLeft = data.value("nbTokens", 0);
    auto msgFormat = data.at("format").get<std::string>();
    if(!strToMessageFormat.contains(msgFormat))
    {
        spdlog::error("Unknown message format {} received for the Communicator {}. Choose a supported message format.", msgFormat, m_name);
        return false;
    }
    m_msgFormat = strToMessageFormat.at(msgFormat);


    return true;
}