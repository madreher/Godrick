# Build the base library
#=======================================
set(library_MODULE GodrickLib   )
#=======================================

file(GLOB files "*.cpp")

add_library( ${library_MODULE} SHARED ${files} )


target_include_directories( ${library_MODULE}
                            PUBLIC
                               $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>
                               $<INSTALL_INTERFACE:${CMAKE_INSTALL_PREFIX}/include>
                           )

target_link_libraries( ${library_MODULE}
                            PUBLIC
                                GR_project_libraries
                                GR_project_options
                                GR_project_warnings
                     )

target_link_libraries( ${library_MODULE}
                         PRIVATE
                            GR_project_warnings
                            GR_project_options
                  )
target_compile_features(   ${library_MODULE} PUBLIC cxx_std_20)

include(GNUInstallDirs)
install(TARGETS ${library_MODULE} EXPORT godrick DESTINATION ${CMAKE_INSTALL_LIBDIR})

if(${GR_MPI_TRANSPORT})
    add_subdirectory(mpi)
    target_link_libraries(${library_MODULE} PUBLIC GodrickMPILib)
endif()
if(${GR_ZMQ_TRANSPORT})
    add_subdirectory(zmq)
    target_link_libraries(${library_MODULE} PUBLIC GodrickZMQLib)
endif()