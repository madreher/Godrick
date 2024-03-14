#include <godrick/port.h>

bool godrick::OutputPort::push(conduit::Node& data) const
{
    bool result = true;
    for(const auto & comm : m_communicators)
        result &= comm->send(data);

    return result;
}

void godrick::OutputPort::flush() const
{
    for(auto & comm : m_communicators)
        comm->flush();
}

bool godrick::InputPort::get(std::vector<conduit::Node>&  data) const
{
    bool result = true;
    for(const auto & comm : m_communicators)
        result &= comm->receive(data);

    return result;
}