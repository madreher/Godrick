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
    return true;
}