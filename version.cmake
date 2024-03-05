# Do not change this value
set(GR_VERSION_MAJOR  0     CACHE NUMBER "Major Version Number")

# Change this if you have added a new feature
set(GR_VERSION_MINOR  0     CACHE NUMBER "Minor Version Number")

# Change this if you have fixed a bug
set(GR_VERSION_PATCH  1     CACHE NUMBER "Patch NUMBER")

execute_process(COMMAND            git rev-list --count HEAD
                WORKING_DIRECTORY  ${CMAKE_SOURCE_DIR}
                OUTPUT_VARIABLE    git_commit_count
                OUTPUT_STRIP_TRAILING_WHITESPACE
)

# This is only changed through the CI system
set(GR_VERSION_BUILD  ${git_commit_count}     CACHE NUMBER "Build version number. This value should be equal to the number of git commits using: git rev-list --count HEAD")
set(GR_VERSION_STRING ${GR_VERSION_MAJOR}.${GR_VERSION_MINOR}.${GR_VERSION_PATCH}.${GR_VERSION_BUILD} CACHE STRING "The final version number")