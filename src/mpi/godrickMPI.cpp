#include <godrick/mpi/godrickMPI.h>
#include <godrick/mpi/utilsMPI.h>
#include <godrick/communicatorFactory.h>


#include <fstream>
#include <sstream>

#include <spdlog/spdlog.h>

#include <nlohmann/json.hpp>
using json = nlohmann::json;

bool godrick::mpi::GodrickMPI::initFromJSON(const std::string& jsonPath, const std::string& taskName)
{
    // Dev note: everything above this should be done by the base class, and only this specific to the MPI version
    // of the handler should be done here.

    // Open the document and check for validity
    std::ifstream file(jsonPath);
    if(!file)
    {
        spdlog::error("Unable to open the configuration file {}.", jsonPath);
    } 

    // Read the entire document
    std::ostringstream ss;
    ss << file.rdbuf();

    // Parse the document and look for the local task information
    json data = json::parse(ss.str());
    if(data.empty())
    {
        spdlog::error("Enable to parse the configuration file {}.", jsonPath);
        return false;
    }

    if(data.count("tasks") == 0)
    {
        spdlog::error("Tasks not found in the configuration file {}.", jsonPath);
        return false;
    }

    // Processing the tasks
    for(auto & task : data["tasks"])
    {
        if (task.count("name") == 0)
        {
            spdlog::error("Unable to find the name of a task.");
            return false;
        }
        auto name = task.at("name").get<std::string>();
        if(name.compare(taskName) != 0)
            continue;
        spdlog::info("Found the task information for the current task.");
        auto taskType = task.at("type").get<std::string>();
        if(taskType.compare("MPI") != 0)
        {
            spdlog::error("Wrong task type associated with the task. This reader can only process MPI tasks.");
            return false;
        }

        // Setup the port
        if(task.count("inputPorts") > 0)
        {
            for(auto & inputPort : task["inputPorts"])
                m_inputPorts.emplace(inputPort, inputPort); // Create a key and a InputPort object from the constructor
        }

        if(task.count("outputPorts") > 0)
        {
            for(auto & outputPort : task["outputPorts"])
                m_outputPorts.emplace(outputPort, outputPort); // Create a key and a OutputPort object from the constructor
        }
        
        if(!initMPIInfo(task.at("startRank").get<int>(), task.at("nbRanks").get<int>()))
        {
            spdlog::error("Something went wrong when trying to setup the MPI communicator for the task {}.", name);
            return false;
        }
    }

    // Processing the communicator
    if(data.count("communicators") > 0)
    {

        for(auto & comm : data["communicators"])
        {
            if(comm["inputTaskName"].get<std::string>().compare(taskName) == 0 || comm["outputTaskName"].get<std::string>().compare(taskName) == 0)
            {
                // This communicator is associated with the local task, processing it
                spdlog::info("Found the communicator {} associated with the local task {}.", comm["name"].get<std::string>(), taskName);

                auto commObj = godrick::createCommunicator(comm["type"].get<std::string>());
                if(!commObj)
                {
                    spdlog::error("Unable to create the communicator {} (something wrong in the json configuration file?).", comm["name"].get<std::string>());
                    return false;
                }
                commObj->initFromJSON(comm, taskName);

                // Assign the communicator to its port.
                if(comm["inputTaskName"].get<std::string>().compare(taskName) == 0)
                {
                    auto portName = comm["inputPortName"].get<std::string>();
                    if(m_inputPorts.count(portName) == 0)
                    {
                        spdlog::error("The input port {} requested by communicator {} doesn't exist for the task {}.", portName, comm["name"], taskName);
                        return false;
                    }
                    m_inputPorts.at(portName).addCommunicator(commObj);
                }
                else
                {
                    auto portName = comm["outputPortName"].get<std::string>();
                    if(m_outputPorts.count(portName) == 0)
                    {
                        spdlog::error("The output port {} requested by communicator {} doesn't exist for the task {}.", portName, comm["name"], taskName);
                        return false;
                    }
                    m_outputPorts.at(portName).addCommunicator(commObj);
                }

                spdlog::info("Communicator {} processed by task {}.", comm["name"].get<std::string>(), taskName);
            }
        }
    }

    return true;
}

bool godrick::mpi::GodrickMPI::initMPIInfo(int startRank, int nbRanks)
{
    m_globalTaskStartRank = startRank;
    m_globalTaskCommSize = nbRanks;

    // Check if MPI must be initialized
    int flagInit;
    int result = MPI_Initialized(&flagInit);
    if(result != MPI_SUCCESS)
    {
        spdlog::error("Something went wrong when checking if MPI is initialized.");
        return false;
    }

    if(!flagInit)
    {
        spdlog::info("Initializing MPI.");
        MPI_Init(nullptr, nullptr);
    }

    m_taskComm = godrick::mpi::utils::collectiveCreateSubCommunicator(MPI_COMM_WORLD, m_globalTaskStartRank, m_globalTaskStartRank + m_globalTaskCommSize - 1);
    MPI_Comm_rank(m_taskComm, &m_taskRank);

    return true;
}

void godrick::mpi::GodrickMPI::close()
{
    MPI_Barrier(MPI_COMM_WORLD);
    MPI_Finalize();
}