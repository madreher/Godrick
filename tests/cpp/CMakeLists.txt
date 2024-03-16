enable_testing()

#Create the base executable to replace the default one from catch
add_library(               GR-catchmain SHARED ${CMAKE_CURRENT_SOURCE_DIR}/catch-main.cpp)
target_link_libraries(     GR-catchmain PUBLIC GR_project_options CONAN_PKG::catch2 GodrickLib GodrickMPILib)
target_compile_features(   GR-catchmain PUBLIC cxx_std_20)
target_compile_definitions(GR-catchmain PUBLIC CATCH_CONFIG_ENABLE_BENCHMARKING)

add_library(               GR-catchmain-mpi SHARED ${CMAKE_CURRENT_SOURCE_DIR}/catch-main-mpi.cpp)
target_link_libraries(     GR-catchmain-mpi PUBLIC GR_project_options CONAN_PKG::catch2 MPI::MPI_CXX GodrickLib GodrickMPILib)
target_compile_features(   GR-catchmain-mpi PUBLIC cxx_std_20)
target_compile_definitions(GR-catchmain-mpi PUBLIC CATCH_CONFIG_ENABLE_BENCHMARKING)

set(LINKED_TARGETS GR-catchmain-mpi)

# Find all files named unit-*.cpp
file(GLOB files "unit-*.cpp")

foreach(file ${files})

    get_filename_component(file_basename ${file} NAME_WE)
    string(REGEX REPLACE "unit-([^$]+)" "test-\\1" testcase ${file_basename})

    string(REGEX REPLACE "unit-([^$]+)" "unit-\\1" exe_name ${file_basename})


    set(UNIT_EXE_NAME  ${exe_name} )
    set(UNIT_TEST_NAME test-${exe_name} )

    add_executable( ${UNIT_EXE_NAME}  ${file} )

    if(MACOSX)
        set_target_properties(${UNIT_EXE_NAME} 
            PROPERTIES
                BUILD_RPATH ${CMAKE_CURRENT_BINARY_DIR}
                INSTALL_RPATH ${CMAKE_INSTALL_PREFIX}/lib    
            )
    endif()

    target_link_libraries( ${UNIT_EXE_NAME}  ${LINKED_TARGETS})

    add_test(  NAME    ${UNIT_TEST_NAME}
               COMMAND mpiexec -n 4 --oversubscribe ${UNIT_EXE_NAME}
            )
    message("New File: ${file} Test case: ${UNIT_TEST_NAME} Exe name: ${UNIT_EXE_NAME}")
endforeach()

# Copy the data folder to the build directory 
file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/data DESTINATION ${CMAKE_CURRENT_BINARY_DIR})