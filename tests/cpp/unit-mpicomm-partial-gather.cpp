#include <catch2/catch.hpp>

#include <godrick/mpi/godrickMPI.h>
#include <spdlog/spdlog.h>

#include <filesystem>

SCENARIO("MPI transport with Partial Gather protocol.")
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
    std::string configPath = "data/config.MPIPartialGatherWorkflow.json";
    REQUIRE(std::filesystem::exists(configPath));

    auto handler = godrick::mpi::GodrickMPI();

    if(rank < 3)
    {
        // Sender code
        std::string taskName = "sendPartial";
        REQUIRE(handler.initFromJSON(configPath, taskName));

        // Sending the data
        conduit::Node data;
        uint32_t val = 10 * static_cast<uint32_t>(rank);
        data["data"] = val;
        data.print_detailed();
        REQUIRE(handler.push("out", data));

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
        REQUIRE(receivedData.size() == 3);
        REQUIRE(receivedData[0]["data"].as_uint32() == 0);
        REQUIRE(receivedData[1]["data"].as_uint32() == 10);
        REQUIRE(receivedData[2]["data"].as_uint32() == 20);

        // Closing the application
        handler.close();
    }
}