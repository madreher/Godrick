#include <catch2/catch.hpp>

#include <godrick/mpi/godrickMPI.h>
#include <spdlog/spdlog.h>

#include <filesystem>

SCENARIO("MPI transport with Partial Broadcast protocol.")
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
    std::string configPath = "data/config.MPIPartialBcastWorkflow.json";
    REQUIRE(std::filesystem::exists(configPath));

    auto handler = godrick::mpi::GodrickMPI();

    if(rank == 0)
    {
        // Sender code
        std::string taskName = "sendPartial";
        REQUIRE(handler.initFromJSON(configPath, taskName));

        // Sending the data
        conduit::Node data;
        uint32_t val = 10;
        data["data"] = val;
        data.print_detailed();
        REQUIRE(handler.push("out", data));
        handler.flush("out");

        // Second data
        conduit::Node data2;
        uint32_t val2 = 20;
        data2["data"] = val2;
        data2.print_detailed();
        REQUIRE(handler.push("out", data2));
        handler.flush("out");

        // Closing the application
        handler.close();
    }
    else 
    {
        // Receiver code
        std::string taskName = "receivePartial";
        REQUIRE(handler.initFromJSON(configPath, taskName));

        // Receiving the data
        std::vector<conduit::Node> receivedData;
        REQUIRE(handler.get("in", receivedData));
        
        // Check the data received 
        REQUIRE(receivedData.size() == 1);
        uint32_t val = 10;
        REQUIRE(receivedData[0]["data"].as_uint32() == val);

        // Receive the second data
        receivedData.clear();
        REQUIRE(handler.get("in", receivedData));

        // Check the data received 
        REQUIRE(receivedData.size() == 1);
        uint32_t val2 = 20;
        REQUIRE(receivedData[0]["data"].as_uint32() == val2);

        // Closing the application
        handler.close();
    }
}