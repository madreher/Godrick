#define CATCH_CONFIG_RUNNER
#include <catch2/catch.hpp>
#include <mpi.h>

int main( int argc, char* argv[] ) {
    MPI_Init(&argc, &argv);
    int result = Catch::Session().run( argc, argv );

    // Not finalizing here, godrick will call finalize when closing.
    //MPI_Finalize();
    return result;
}
