#pragma once 

#include <string>
#include <vector>
#include <memory>

#include <conduit/conduit.hpp>

#include <godrick/communicator.h>


namespace godrick {

class Port
{
public:
    Port(const std::string& name) : m_name(name){}
    virtual ~Port(){}
    virtual void addCommunicator(std::shared_ptr<Communicator> comm) { m_communicators.push_back(comm); }


protected:
    std::vector<std::shared_ptr<Communicator> > m_communicators;
    std::string m_name;
};

class InputPort : public Port
{
public:
    InputPort(const std::string& name) : Port(name){}
    virtual ~InputPort() override {}
    bool get(std::vector<conduit::Node>&  data) const;
};

class OutputPort : public Port 
{
public:
    OutputPort(const std::string& name) : Port(name){}
    virtual ~OutputPort() override {}
    bool push(conduit::Node& data) const;
};

} // godrick