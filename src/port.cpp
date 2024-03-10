#include <godrick/port.h>

bool godrick::OutputPort::push(conduit::Node& data) const
{
    bool result = true;
    for(const auto & comm : m_communicators)
        result &= comm->send(data);

    return result;
}

bool godrick::InputPort::get(std::vector<conduit::Node>&  data) const
{
    bool result = true;
    for(const auto & comm : m_communicators)
        result &= comm->receive(data);

    return result;
}