#include <godrick/port.h>

#include <stdexcept>

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

void godrick::InputPort::addCommunicator(std::shared_ptr<Communicator> comm)
{ 
    if(m_communicators.size() > 0)
        throw std::invalid_argument("Input port can only accept a single communicator.");
    m_communicators.push_back(comm); 
}

godrick::MessageResponse godrick::InputPort::get(std::vector<conduit::Node>&  data)
{
    //bool result = true;
    //for(const auto & comm : m_communicators)
    //    result &= comm->receive(data);
    //
    //return result;
    if(m_communicators.empty())
        return godrick::MessageResponse::EMPTY;
    else
        // Input ports only have a single communicator, accessing it directly
        return m_communicators[0]->receive(data);
}