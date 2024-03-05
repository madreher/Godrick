# from here:
#
# https://github.com/lefticus/cppbestpractices/blob/master/02-Use_the_Tools_Avai
# lable.md

function(set_coverage_flags project_name)

  option(MQ_ENABLE_COVERAGE "Enable Code Coverage" TRUE)

  if( MQ_ENABLE_COVERAGE )

    if(CMAKE_COMPILER_IS_GNUCC)

        target_compile_options(${project_name}  INTERFACE --coverage -g -O0 -fprofile-arcs -ftest-coverage)
        target_link_libraries( ${project_name}  INTERFACE --coverage -g -O0 -fprofile-arcs -ftest-coverage)

        add_custom_target(coverage
            COMMAND rm -rf coverage
            COMMAND mkdir -p coverage
            #COMMAND gcovr -r ${CMAKE_SOURCE_DIR} --filter ${CMAKE_SOURCE_DIR}/src ${exclude_flags} --exclude ${CMAKE_SOURCE_DIR}/src/lib/nd2ImGuiSystem --exclude ${CMAKE_SOURCE_DIR}/src/lib/nd2Renderer --exclude ${CMAKE_SOURCE_DIR}/src/lib/nd2UISystem --exclude ${CMAKE_SOURCE_DIR}/src/lib/nd2ActionSystem/include/nfcbn/nd2/Process --html-details --html -o coverage/index.html
            #COMMAND gcovr -r ${CMAKE_SOURCE_DIR} --filter ${CMAKE_SOURCE_DIR}/src ${exclude_flags} --exclude ${CMAKE_SOURCE_DIR}/src/lib/nd2ImGuiSystem --exclude ${CMAKE_SOURCE_DIR}/src/lib/nd2Renderer --exclude ${CMAKE_SOURCE_DIR}/src/lib/nd2UISystem --exclude ${CMAKE_SOURCE_DIR}/src/lib/nd2ActionSystem/include/nfcbn/nd2/Process --xml -o coverage/report.xml
            #COMMAND gcovr -r ${CMAKE_SOURCE_DIR} --filter ${CMAKE_SOURCE_DIR}/src ${exclude_flags} --exclude ${CMAKE_SOURCE_DIR}/src/lib/nd2ImGuiSystem --exclude ${CMAKE_SOURCE_DIR}/src/lib/nd2Renderer --exclude ${CMAKE_SOURCE_DIR}/src/lib/nd2UISystem --exclude ${CMAKE_SOURCE_DIR}/src/lib/nd2ActionSystem/include/nfcbn/nd2/Process -o coverage/report.txt
            COMMAND cat coverage/report.txt
            WORKING_DIRECTORY ${CMAKE_BINARY_DIR}  # Need separate command for this line
        )

    endif()

  endif()

endfunction()
