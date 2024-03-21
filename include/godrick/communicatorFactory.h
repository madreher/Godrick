#pragma once

#include <memory>
#include <godrick/communicator.h>

namespace godrick 
{

std::shared_ptr<godrick::Communicator> createCommunicator(const std::string& type);

} // godrick