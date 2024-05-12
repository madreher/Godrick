# Build the base library
#=======================================
set(library_MODULE GodrickLib   )
#=======================================

file(GLOB files "*.cpp")

if(${GR_MPI_TRANSPORT})
    file(GLOB filesmpi "mpi/*.cpp")
    list(APPEND files ${filesmpi})
endif()

if(${GR_ZMQ_TRANSPORT})
    file(GLOB filesmpi "zmq/*.cpp")
    list(APPEND files ${filesmpi})
endif()

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
if(${GR_MPI_TRANSPORT})
target_compile_definitions(${library_MODULE} 
                            PUBLIC
                                GODRICK_MPI)
target_link_libraries( ${library_MODULE}
                            PUBLIC
                                conduit::conduit_mpi
                                MPI::MPI_CXX
                    )
endif()
if(${GR_ZMQ_TRANSPORT})
target_compile_definitions(${library_MODULE} 
                     PUBLIC
                         GODRICK_ZMQ)
target_link_libraries( ${library_MODULE}
                            PUBLIC
                                CONAN_PKG::cppzmq
                     )
endif()
target_link_libraries( ${library_MODULE}
                         PRIVATE
                            GR_project_warnings
                            GR_project_options
                  )
target_compile_features(   ${library_MODULE} PUBLIC cxx_std_20)

include(GNUInstallDirs)
install(TARGETS ${library_MODULE} EXPORT godrick DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(DIRECTORY ${CMAKE_SOURCE_DIR}/include/godrick 
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
        PATTERN "include/godrick/mpi" EXCLUDE
        PATTERN "include/godrick/zmq" EXCLUDE)
if(${GR_MPI_TRANSPORT})
install(DIRECTORY ${CMAKE_SOURCE_DIR}/include/godrick/mpi 
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/godrick)
endif()
if(${GR_ZMQ_TRANSPORT})
install(DIRECTORY ${CMAKE_SOURCE_DIR}/include/godrick/zmq 
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/godrick)
endif()
