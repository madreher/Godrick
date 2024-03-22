#include <string>

#include <godrick/mpi/godrickMPI.h>

#include <lyra/lyra.hpp>
#include <spdlog/spdlog.h>

#include <conduit/conduit.hpp>

int main(int argc, char** argv)
{
    std::string taskName;
    std::string configFile;

    auto cli = lyra::cli()
        | lyra::opt( taskName, "name" )
            ["--name"]
            ("Name of the task corresponding to the python workflow definition.")
        | lyra::opt( configFile, "config" )
            ["--config"]
            ("Path to the config file.");

    auto result = cli.parse( { argc, argv } );
    if ( !result )
    {
        spdlog::critical("Unable to parse the command line: {}.", result.errorMessage());
        exit(1);
    }

    spdlog::info("Starting the task {}.", taskName);

    auto handler = godrick::mpi::GodrickMPI();

    spdlog::info("Loading the workflow configuration {}.", configFile);
    if(handler.initFromJSON(configFile, taskName))
        spdlog::info("Configuration file loaded successfully.");
    else
    {
        spdlog::error("Something went wrong during the workflow configuration.");
        exit(-1);
    }

    //auto taskRank = handler.getTaskRank();
    auto taskComm = handler.getTaskCommunicator();
    int taskCommSize;
    MPI_Comm_size(taskComm, &taskCommSize);
    if(taskCommSize != 1)
    {
        spdlog::info("Task {} has to be configured with a single rank ({} detected).", taskName, taskCommSize);
        handler.close();

        return EXIT_FAILURE;
    }

    // Sending the data
    conduit::Node data;
    uint32_t val = 10;
    data["data"] = val;
    data.print_detailed();

    if(handler.push("out", data))
        spdlog::info("Data sent from the send task.");
    else
        spdlog::error("Something went wrong when sending the data.");
    
    
    handler.close();
}