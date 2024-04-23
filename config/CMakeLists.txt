# CMake adapted from the Conduit project 
# conduitSrc/src/config/CMakeLists.txt

if (NOT DEFINED GODRICK_INSTALL_INCLUDE_DIR)
    set(GODRICK_INSTALL_INCLUDE_DIR "include")
endif()

if (NOT DEFINED GODRICK_INSTALL_CONFIG_DIR)
    set(GODRICK_INSTALL_CONFIG_DIR "lib")
endif()

if (NOT DEFINED GODRICK_INSTALL_LIB_DIR)
    set(GODRICK_INSTALL_LIB_DIR "lib")
endif()

if (NOT DEFINED GODRICK_INSTALL_BIN_DIR)
    set(GODRICK_INSTALL_BIN_DIR "bin")
endif()

if (NOT DEFINED GODRICK_INSTALL_CMAKE_MODULE_DIR)
  set(GODRICK_INSTALL_CMAKE_MODULE_DIR "${GODRICK_INSTALL_CONFIG_DIR}/cmake")
endif()

include(CMakePackageConfigHelpers)

# write version heler
write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/GodrickConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY AnyNewerVersion
)


# setup cmake package config file
configure_package_config_file(
  GodrickConfig.cmake.in
  ${CMAKE_CURRENT_BINARY_DIR}/GodrickConfig.cmake
  INSTALL_DESTINATION ${GODRICK_INSTALL_CONFIG_DIR}
  PATH_VARS
    GODRICK_INSTALL_INCLUDE_DIR
    GODRICK_INSTALL_LIB_DIR
    GODRICK_INSTALL_BIN_DIR
    GODRICK_INSTALL_CMAKE_MODULE_DIR
    )


# install everything needed

# install exports to comply with standard find_package search path expectations
install(FILES
        ${CMAKE_CURRENT_BINARY_DIR}/GodrickConfig.cmake
        ${CMAKE_CURRENT_BINARY_DIR}/GodrickConfigVersion.cmake
        godrick_define_targets.cmake
        DESTINATION ${GODRICK_INSTALL_CMAKE_MODULE_DIR}/godrick/)