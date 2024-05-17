add_executable(sendPartial send.cpp)

target_link_libraries(sendPartial
                                GR_project_libraries
                                GR_project_options
                                GR_project_warnings
                                GodrickLib)

add_executable(receivePartial receive.cpp)

target_link_libraries(receivePartial
                                GR_project_libraries
                                GR_project_options
                                GR_project_warnings
                                GodrickLib)

install(TARGETS 
            sendPartial
            receivePartial
        DESTINATION
            ${GR_EXAMPLES_DIR}/mpipartialbcastgather/bin)

install(FILES 
                    simplempi_partial_bcast_workflow.py
                    simplempi_partial_gather_workflow.py
            DESTINATION 
                    ${GR_EXAMPLES_DIR}/mpipartialbcastgather)