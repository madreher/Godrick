cmake_minimum_required(VERSION 3.15)


################################################################################
include(version.cmake)
################################################################################

# Set the project name to your project name, my project isn't very descriptive
project(Godrick
        VERSION
            ${GR_VERSION_MAJOR}.${GR_VERSION_MINOR}.${GR_VERSION_PATCH}
        )

# Reference for RPATH with conan: https://docs.conan.io/1/howtos/manage_shared_libraries/rpaths.html
if( EXISTS ${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake )
    include(${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake)
    conan_basic_setup(NO_OUTPUT_DIRS TARGETS KEEP_RPATHS)
else()
    message(FATAL_ERROR "\n\nERROR: \nConan config file not found. You need to call the following from the build directory first: \n  conan profile new qt_cmake_autodetect --detect --force\n  conan install -s compiler.libcxx=libstdc++11  ${CMAKE_SOURCE_DIR} --build missing")
endif()

#########################################################
# Buid options
#########################################################

set(GR_MPI_TRANSPORT                TRUE CACHE BOOL "Compile with support for MPI tasks and communicators.")
set(GR_ZMQ_TRANSPORT                TRUE CACHE BOOL "Compile with support for ZMQ communicators.")
set(GR_ENABLE_CPP_COVERAGE          FALSE CACHE BOOL "Enable coverage for c++ code.")

#########################################################
# Other targets
#########################################################
add_custom_target( ${PROJECT_NAME}_other_files
                        SOURCES
                           README.md
                           run_cmake_script.sh
                           conanfile.txt
                           cmake/CompilerWarnings.cmake
                           cmake/Coverage.cmake
                           cmake/StandardProjectSettings.cmake
                           .gitignore
                )
#########################################################

include(GNUInstallDirs)
include(cmake/StandardProjectSettings.cmake)

#######################################################################################
# standard compiler warnings
add_library(GR_project_warnings INTERFACE)
include(cmake/CompilerWarnings.cmake)
set_project_warnings(GR_project_warnings)
#######################################################################################

#######################################################################################
# Link this 'library' to set the c++ standard / compile-time options requested
add_library(GR_project_options INTERFACE)
#######################################################################################
target_compile_features(GR_project_options INTERFACE cxx_std_20)

target_compile_definitions(GR_project_options
                            INTERFACE
                                GR_CMAKE_BINARY_DIR="${CMAKE_BINARY_DIR}"
                                GR_CMAKE_SOURCE_DIR="${CMAKE_SOURCE_DIR}"
                                GR_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}"
                                GR_BUILD_DIR="${CMAKE_CURRENT_BINARY_DIR}"
                                GR_VERSION_STRING="${GR_VERSION_STRING}"
                                GR_VERSION_MAJOR=${GR_VERSION_MAJOR}
                                GR_VERSION_MINOR=${GR_VERSION_MINOR}
                                GR_VERSION_PATCH=${GR_VERSION_PATCH}
                                GR_VERSION_TWEAK=${GR_VERSION_BUILD}
                                GR_CMAKE_INSTALL_PREFIX="${CMAKE_INSTALL_PREFIX}"
                                GR_GIT_COMMIT_HASH="${GIT_COMMIT_HASH}")

#######################################################################################
# Link this interface to include a standard set of libs that would be needed
# for developing Godrick
#######################################################################################
add_library(GR_project_libraries INTERFACE )
#######################################################################################

target_include_directories( GR_project_libraries
    INTERFACE
        $<BUILD_INTERFACE:${CMAKE_SOURCE_DIR}/include>  
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_PREFIX}/include>)

# This is necessary to do here because MPI has to be found BEFORE
# finding Conduit. Otherwise, Conduit seems to hide/overwrite the MPI cmake variables 
if(${GR_MPI_TRANSPORT})
    find_package(MPI REQUIRED)
endif()


if (${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    set(MACOSX TRUE)
endif()

find_package(Conduit REQUIRED)        
if(WIN32)
target_link_libraries( GR_project_libraries
    INTERFACE
        CONAN_PKG::spdlog
        CONAN_PKG::lyra
        CONAN_PKG::nlohmann_json
        conduit::conduit
)
elseif(MACOSX)
target_link_libraries( GR_project_libraries
    INTERFACE
        CONAN_PKG::spdlog
        CONAN_PKG::lyra
        CONAN_PKG::nlohmann_json
        conduit::conduit
)
else()
target_link_libraries( GR_project_libraries
    INTERFACE
        CONAN_PKG::spdlog
        CONAN_PKG::lyra
        CONAN_PKG::nlohmann_json
        stdc++fs
        conduit::conduit
)
endif()

# Explicitely settings these dummy interfaces as export for the package 
# so that the cmake godrick.cmake can be generated at the end
install(TARGETS GR_project_libraries 
        EXPORT godrick
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin)
install(TARGETS GR_project_options EXPORT godrick)
install(TARGETS GR_project_warnings EXPORT godrick)

set(GR_BIN_DIR 			${CMAKE_INSTALL_PREFIX}/bin)
set(GR_LIB_DIR 			${CMAKE_INSTALL_PREFIX}/lib)
set(GR_EXAMPLES_DIR     ${CMAKE_INSTALL_PREFIX}/examples)

# Coverage setup if enable 
if(${GR_ENABLE_CPP_COVERAGE})

    # Force build to debug and add coverage flags
    set(CMAKE_BUILD_TYPE Debug)
    set(CMAKE_CXX_FLAGS "-O0 -coverage")

    # Look for the necessary utility programs
    find_program(LCOV lcov REQUIRED)
    find_program(GENHTML genhtml REQUIRED)
    
    # Add coverage target 
    add_custom_target(coverage
    # gather data
    COMMAND ${LCOV} --directory ${CMAKE_SOURCE_DIR} --capture --output-file coverage.info --no-external
    # generate report
    COMMAND ${GENHTML} --demangle-cpp -o coverage coverage.info
    WORKING_DIRECTORY ${CMAKE_BINARY_DIR})
endif()

add_subdirectory(src)
add_subdirectory(examples)

enable_testing()
add_subdirectory(tests)

install(DIRECTORY data DESTINATION ${CMAKE_INSTALL_PREFIX})

include(GNUInstallDirs)
#install(DIRECTORY include/godrick DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

################################
# Add our config helpers
################################
add_subdirectory(config)

################################
# Create CMake importable
# exports for all of our targets
################################
# install exports to comply with standard find_package search path expectations
install(EXPORT godrick DESTINATION lib/cmake/godrick)