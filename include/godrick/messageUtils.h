#pragma once

#include <conduit/conduit.hpp>

namespace godrick {

void setTerminateMessage(conduit::Node& data);
bool isTerminateMessage(const conduit::Node& data);

} // godrick