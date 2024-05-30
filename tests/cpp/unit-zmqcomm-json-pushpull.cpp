#include <catch2/catch.hpp>

#include <godrick/mpi/godrickMPI.h>
#include <spdlog/spdlog.h>

#include <zmq.hpp>

#include <filesystem>

SCENARIO("ZMQ transport with JSON Format and PUSH_PULL protocol.")
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
        MPI_Barrier(MPI_COMM_WORLD);
        MPI_Finalize();
        return;
    }

    // Check that the config file exist
    std::string configPath = "data/config.ZMQJSONPushPullWorkflow.json";
    REQUIRE(std::filesystem::exists(configPath));

    auto handler = godrick::mpi::GodrickMPI();

    if(rank == 0)
    {
        // Sender code
        std::string taskName = "sendpushpull";
        REQUIRE(handler.initFromJSON(configPath, taskName));

        // Sending the data
        conduit::Node data;
        uint32_t val = 10;
        data["data"] = val;
        data.print_detailed();
        REQUIRE(handler.push("out", data));
        handler.flush("out");

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
        REQUIRE(handler.get("in", receivedData) == godrick::MessageResponse::MESSAGES);
        
        // Check the data received 
        REQUIRE(receivedData.size() == 1);
        uint32_t val = 10;
        // Conduit try to guess the type when reading from JSON but won't get the exact same type as the origin
        // Preserving the original type is probably only possible by using the json conduit format (not simple json format)
        // The JSON format is just meant to be used to communicate with outside application where exact type doesn't really matter
        REQUIRE(receivedData[0]["data"].as_int64() == val); 

        // Closing the application
        handler.close();
    }
}