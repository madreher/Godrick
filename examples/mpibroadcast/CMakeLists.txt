add_executable(send send.cpp)

target_link_libraries(send
                                GR_project_libraries
                                GR_project_options
                                GR_project_warnings
                                GodrickLib)
                                #GodrickMPILib)

add_executable(receive receive.cpp)

target_link_libraries(receive
                                GR_project_libraries
                                GR_project_options
                                GR_project_warnings
                                GodrickLib)
                                #GodrickMPILib)

install(TARGETS 
            send
            receive
        DESTINATION
            ${GR_EXAMPLES_DIR}/mpibroadcast/bin)

install(FILES 
                    simplempi_ports_workflow.py
            DESTINATION 
                    ${GR_EXAMPLES_DIR}/mpibroadcast)