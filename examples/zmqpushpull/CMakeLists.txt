add_executable(sendpushpull send.cpp)

target_link_libraries(sendpushpull
                                GR_project_libraries
                                GR_project_options
                                GR_project_warnings
                                GodrickLib
                                GodrickMPILib
                                GodrickZMQLib)

add_executable(receivepushpull receive.cpp)

target_link_libraries(receivepushpull
                                GR_project_libraries
                                GR_project_options
                                GR_project_warnings
                                GodrickLib
                                GodrickMPILib
                                GodrickZMQLib)

install(TARGETS 
            sendpushpull
            receivepushpull
        DESTINATION
            ${GR_EXAMPLES_DIR}/zmqpushpull/bin)

install(FILES 
                    zmq_pushpull_workflow.py
            DESTINATION 
                    ${GR_EXAMPLES_DIR}/zmqpushpull)