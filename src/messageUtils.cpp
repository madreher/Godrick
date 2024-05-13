#include <godrick/messageUtils.h>

void godrick::setTerminateMessage(conduit::Node& data)
{
    uint8_t val = 0;
    data["godrick"]["terminate"] = val;
    return;
}

bool godrick::isTerminateMessage(const conduit::Node& data)
{
    return data.has_path("godrick/terminate");
}