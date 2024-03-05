#=======================================
set(library_MODULE GodrickMPILib   )
#=======================================

find_package(MPI REQUIRED)

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
                                MPI::MPI_CXX
                     )

target_link_libraries( ${library_MODULE}
                         PRIVATE
                            GR_project_warnings
                            GR_project_options
                  )
target_compile_features(   ${library_MODULE} PUBLIC cxx_std_20)