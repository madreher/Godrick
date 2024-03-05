cmake_minimum_required(VERSION 3.15)


################################################################################
include(version.cmake)
################################################################################

# Set the project name to your project name, my project isn't very descriptive
project(Godrick
        VERSION
            ${GR_VERSION_MAJOR}.${GR_VERSION_MINOR}.${GR_VERSION_PATCH}
        )

if( EXISTS ${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake )
    include(${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake)
    conan_basic_setup(NO_OUTPUT_DIRS TARGETS)
else()
    message(FATAL_ERROR "\n\nERROR: \nConan config file not found. You need to call the following from the build directory first: \n  conan profile new qt_cmake_autodetect --detect --force\n  conan install -s compiler.libcxx=libstdc++11  ${CMAKE_SOURCE_DIR} --build missing")
endif()

#########################################################
# Buid options
#########################################################

set(GR_MPI_TRANSPORT TRUE CACHE BOOL "Compile with support for MPI tasks and communicators.")

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
                                CMAKE_BINARY_DIR="${CMAKE_BINARY_DIR}"
                                CMAKE_SOURCE_DIR="${CMAKE_SOURCE_DIR}"
                                MQ_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}"
                                MQ_BUILD_DIR="${CMAKE_CURRENT_BINARY_DIR}"
                                MQ_VERSION_STRING="${MQ_VERSION_STRING}"
                                MQ_VERSION_MAJOR=${MQ_VERSION_MAJOR}
                                MQ_VERSION_MINOR=${MQ_VERSION_MINOR}
                                MQ_VERSION_PATCH=${MQ_VERSION_PATCH}
                                MQ_VERSION_TWEAK=${MQ_VERSION_BUILD}
                                CMAKE_INSTALL_PREFIX="${CMAKE_INSTALL_PREFIX}"
                                MQ_GIT_COMMIT_HASH="${GIT_COMMIT_HASH}")

#######################################################################################
# Link this interface to include a standard set of libs that would be needed
# for developing Nanodesigner
#######################################################################################
add_library(GR_project_libraries INTERFACE )
#######################################################################################

target_include_directories( GR_project_libraries
    INTERFACE
        ${CMAKE_SOURCE_DIR}/include)
if(WIN32)
target_link_libraries( GR_project_libraries
    INTERFACE
        CONAN_PKG::spdlog
        CONAN_PKG::lyra
        CONAN_PKG::nlohmann_json
)
else()
target_link_libraries( GR_project_libraries
    INTERFACE
        CONAN_PKG::spdlog
        CONAN_PKG::lyra
        CONAN_PKG::nlohmann_json
        stdc++fs
)
endif()

set(GR_BIN_DIR 			${CMAKE_INSTALL_PREFIX}/bin)
set(GR_LIB_DIR 			${CMAKE_INSTALL_PREFIX}/lib)

add_subdirectory(src)
