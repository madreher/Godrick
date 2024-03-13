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

    std::vector<conduit::Node> receivedData;
    if(handler.get("in", receivedData))
    {
        if(receivedData.size() == 1)
        {   
            spdlog::info("Received {} conduit nodes.", receivedData.size());
            receivedData[0].print_detailed();
        }
        else
        {
            spdlog::error("The receiver received something different than 1 conduit node during a broadcast.");
        }
    }
    else 
        spdlog::error("Something went wrong when receiving data.");

    
    handler.close();
}