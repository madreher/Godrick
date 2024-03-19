#include <catch2/catch.hpp>

#include <godrick/mpi/godrickMPI.h>
#include <spdlog/spdlog.h>

#include <filesystem>

SCENARIO("Check ports used during MPI transport with Broadcast protocol.")
{
    int size_world, rank;
    MPI_Comm_size(MPI_COMM_WORLD, &size_world);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    if( size_world != 4 )
    {
        spdlog::error("Unit test mpi broadcast requires 4 mpi processes." );
        REQUIRE(false);
        return;
    }

    // Check that the config file exist
    std::string configPath = "data/config.MPIBroadcastWorkflow.json";
    REQUIRE(std::filesystem::exists(configPath));

    auto handler = godrick::mpi::GodrickMPI();

    if(rank == 0)
    {
        // Sender code
        std::string taskName = "send";
        REQUIRE(handler.initFromJSON(configPath, taskName));

        // Check the ports
        auto inputList = handler.getInputPortList();
        auto outputList = handler.getOutputPortList();

        REQUIRE(inputList.size() == 0);
        REQUIRE(outputList.size() == 1);
        REQUIRE(outputList[0].compare("out") == 0);

        // Closing the application
        handler.close();
    }
    else 
    {
        // Receiver code
        std::string taskName = "receive";
        REQUIRE(handler.initFromJSON(configPath, taskName));
        
        // Check the ports
        auto inputList = handler.getInputPortList();
        auto outputList = handler.getOutputPortList();

        REQUIRE(inputList.size() == 1);
        REQUIRE(outputList.size() == 0);
        REQUIRE(inputList[0].compare("in") == 0);

        // Closing the application
        handler.close();
    }
}