#pragma once

#include <string>

namespace godrick {

class Godrick
{

public:
    Godrick(){}
    virtual ~Godrick(){}
    virtual bool initFromJSON(const std::string& jsonPath, const std::string& taskName);

    virtual void close(){}

protected:


}; // Godrick

} // godrick