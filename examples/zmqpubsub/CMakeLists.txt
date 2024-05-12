add_executable(sendpubsub send.cpp)

target_link_libraries(sendpubsub
                                GR_project_libraries
                                GR_project_options
                                GR_project_warnings
                                GodrickLib)
                                #GodrickMPILib
                                #GodrickZMQLib)

add_executable(receivepubsub receive.cpp)

target_link_libraries(receivepubsub
                                GR_project_libraries
                                GR_project_options
                                GR_project_warnings
                                GodrickLib)
                                #GodrickMPILib
                                #GodrickZMQLib)

install(TARGETS 
            sendpubsub
            receivepubsub
        DESTINATION
            ${GR_EXAMPLES_DIR}/zmqpubsub/bin)

install(FILES 
                    zmq_pubsub_workflow.py
            DESTINATION 
                    ${GR_EXAMPLES_DIR}/zmqpubsub)