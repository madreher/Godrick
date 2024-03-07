#include <godrick/mpi/godrickMPI.h>
#include <godrick/mpi/utilsMPI.h>

#include <fstream>
#include <sstream>

#include <spdlog/spdlog.h>

#include <nlohmann/json.hpp>
using json = nlohmann::json;

bool godrick::mpi::GodrickMPI::initFromJSON(const std::string& jsonPath, const std::string& taskName)
{
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
    else if(data.count("tasks") > 0)
    {
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
            return initMPIInfo(task.at("startRank").get<int>(), task.at("nbRanks").get<int>());
        }
    }
    else 
    {
        spdlog::error("Tasks not found in the configuration file {}.", jsonPath);
        return false;
    }
    return false;
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
    MPI_Finalize();
}