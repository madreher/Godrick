#=======================================
set(library_MODULE GodrickZMQLib   )
#=======================================

file(GLOB_RECURSE files "*.cpp")

add_library( ${library_MODULE} SHARED ${files} )


target_include_directories( ${library_MODULE}
                            PUBLIC
                               "$<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>"
                           )

target_link_libraries( ${library_MODULE}
                            PUBLIC
                                GR_project_libraries
                                GR_project_options
                                GR_project_warnings
                                CONAN_PKG::cppzmq
                     )

target_compile_definitions(${library_MODULE} 
                     PUBLIC
                         GODRICK_ZMQ)

target_link_libraries( ${library_MODULE}
                         PRIVATE
                            GR_project_warnings
                            GR_project_options
                  )
target_compile_features(   ${library_MODULE} PUBLIC cxx_std_20)

include(GNUInstallDirs)
install(TARGETS ${library_MODULE} DESTINATION ${CMAKE_INSTALL_LIBDIR})