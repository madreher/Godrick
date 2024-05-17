# CMake adapted from the Conduit project 
# conduitSrc/src/config/conduit_setup_targets.cmake

# In the install folder, go back to the root folder
get_filename_component(_IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)

if(_IMPORT_PREFIX STREQUAL "/")
  set(_IMPORT_PREFIX "")
endif()

set(GODRICK_INCLUDE_DIRS "${_IMPORT_ROOT}/include/godrick")

# Create a proxy target and we add to it
add_library(godrick::godrick INTERFACE IMPORTED)

set_property(TARGET godrick::godrick
             APPEND PROPERTY
             INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_ROOT}/include/")

set_property(TARGET godrick::godrick
             PROPERTY INTERFACE_LINK_LIBRARIES
             GodrickLib)

#if(GODRICK_MPI_TRANSPORT)
#    add_library(godrick::godrick_mpi INTERFACE IMPORTED)
#    set_property(TARGET godrick::godrick_mpi
#                PROPERTY INTERFACE_LINK_LIBRARIES
#                godrick::godrick
#                GodrickMPILib)
#endif()

#if(GODRICK_ZMQ_TRANSPORT)
#    add_library(godrick::godrick_zmq INTERFACE IMPORTED)
#    set_property(TARGET godrick::godrick_zmq
#                PROPERTY INTERFACE_LINK_LIBRARIES
#                godrick::godrick
#                GodrickZMQLib)
#endif()

message(STATUS "Found Godrick: ${_IMPORT_ROOT} (found version ${GODRICK_VERSION})")