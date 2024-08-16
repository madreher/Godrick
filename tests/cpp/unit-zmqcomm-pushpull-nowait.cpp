#include <catch2/catch.hpp>

#include <godrick/mpi/godrickMPI.h>
#include <spdlog/spdlog.h>

#include <filesystem>

SCENARIO("ZMQ transport with PUSH_PULL protocol and no wait.")
{
    int size_world, rank;
    MPI_Comm_size(MPI_COMM_WORLD, &size_world);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    if( size_world < 2 )
    {
        spdlog::error("Unit test zmq requires at least 2 processes." );
        REQUIRE(false);
        return;
    }

    if (rank >= 2)
    {
        // The pushpull only uses 2 processes for now but all the unit tests using MPI 
        // have 4 processes. Ignoring the other 2. 

        // Calling Barrier to unlock the unit test barrier
        MPI_Barrier(MPI_COMM_WORLD);

        //Calling Barrier to unlok the handler.close()
        MPI_Barrier(MPI_COMM_WORLD);
        MPI_Finalize();
        return;
    }

    // Check that the config file exist
    std::string configPath = "data/config.ZMQPushPullWorkflowNoWait.json";
    REQUIRE(std::filesystem::exists(configPath));

    auto handler = godrick::mpi::GodrickMPI();

    if(rank == 0)
    {
        // Sender code
        std::string taskName = "sendpushpull";
        REQUIRE(handler.initFromJSON(configPath, taskName));
        
        // Barrier to prevent the receiver to receive the terminate message
        MPI_Barrier(MPI_COMM_WORLD);

        // Closing the application
        handler.close();
    }
    else 
    {
        // Receiver code
        std::string taskName = "receivepushpull";
        REQUIRE(handler.initFromJSON(configPath, taskName));

        // Receiving the data
        std::vector<conduit::Node> receivedData;
        spdlog::info("Waiting for data on rank {}", rank);
        REQUIRE(handler.get("in", receivedData) == godrick::MessageResponse::EMPTY);

        // Barrier to prevent the receiver to receive the terminate message
        MPI_Barrier(MPI_COMM_WORLD);

        // Closing the application
        handler.close();
    }
}