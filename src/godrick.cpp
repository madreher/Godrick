#include <godrick/godrick.h>

#include <nlohmann/json.hpp>
using json = nlohmann::json;

bool godrick::Godrick::initFromJSON(const std::string& jsonPath, const std::string& taskName)
{
    (void)jsonPath;
    (void)taskName;
    return false;
}