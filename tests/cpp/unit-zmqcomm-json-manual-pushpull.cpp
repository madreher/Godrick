#include <catch2/catch.hpp>

#include <godrick/mpi/godrickMPI.h>
#include <spdlog/spdlog.h>

#include <zmq.hpp>

#include <filesystem>

SCENARIO("ZMQ transport with JSON Format and PUSH_PULL protocol on sender only. Received done manually.")
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

        // Manually get the data
        std::string addr = "localhost";
        uint32_t port = 50000;
        std::stringstream ss;
        ss<<"tcp://"<<addr<<":"<<port;

        zmq::context_t context(1);
        auto socket = zmq::socket_t(context, ZMQ_PULL);
        socket.connect(ss.str());

        zmq::message_t msg;
        zmq::recv_result_t result = socket.recv(msg, zmq::recv_flags::none);

        REQUIRE(result.has_value());
        REQUIRE(result.value() != 0);

        std::string msgJSON(static_cast<char*>(msg.data()), msg.size());

        nlohmann::json data = json::parse(msgJSON);
        spdlog::info("{}", msgJSON);
        REQUIRE(data["data"].get<uint32_t>() == 10);



        // Closing the application
        MPI_Barrier(MPI_COMM_WORLD);
        MPI_Finalize();
    }
}