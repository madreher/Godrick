#include <godrick/communicatorFactory.h>

#ifdef GODRICK_MPI
#include <godrick/mpi/communicatorMPI.h>
#endif
#ifdef GODRICK_ZMQ
#include <godrick/zmq/communicatorZMQ.h>
#endif

// Forward declaration. The relevant classes are defined in their own library, not the core library


#include <unordered_map>
#include <spdlog/spdlog.h>

std::shared_ptr<godrick::Communicator> godrick::createCommunicator(const std::string& type)
{
    if(type.compare("MPI") == 0)
    {
#ifdef GODRICK_MPI
        return std::make_shared<godrick::mpi::CommunicatorMPI>();
#else 
        spdlog::error("Godrick was not compiled with MPI support, unable to create a MPI communicator.");
        return nullptr;
#endif
    }
    if(type.compare("ZMQ") == 0)
    {
#ifdef GODRICK_ZMQ
        return std::make_shared<godrick::grzmq::CommunicatorZMQ>();
#else
        spdlog::error("Godrick was not compiled with ZMQ support, unable to create a MPI communicator.");
        return nullptr;
#endif
    }
    
    spdlog::error("Unknown communicator type {}.", type);
    return nullptr;
}