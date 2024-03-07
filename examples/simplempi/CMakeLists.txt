add_executable(task dummytask.cpp)

target_link_libraries(task
                                GR_project_libraries
                                GR_project_options
                                GR_project_warnings
                                GodrickLib
                                GodrickMPILib)

install(TARGETS 
                    task 
                DESTINATION
                    ${GR_EXAMPLES_DIR}/simplempi/bin)

install(FILES 
                    simplempi_workflow.py 
            DESTINATION 
                    ${GR_EXAMPLES_DIR}/simplempi)