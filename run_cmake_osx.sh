#!/bin/bash

# Simple script to build the full application.
#
#
#  cd src_dir
#  mkdir build
#  cd build
#  ../build_script.sh
#

# Change these if you want to use different verions of NFCBN dependencies


# Exit the script if any of the bash commands results in an error
#=============== get the folder where this script resides ==============
# https://stackoverflow.com/questions/59895/get-the-source-directory-of-a-bash-script-from-within-the-script-itself

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done

DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
#==================================================================================


set -e

#DISTRO_CODENAME=$(lsb_release -cs)
#DISTRO_DESCRIPTION=$(lsb_release -ds)

#if [[ "${DISTRO_DESCRIPTION}" == "Linux Mint 19"* ]]; then 
#    DISTRO_CODENAME=bionic
#fi
#if [[ "${DISTRO_DESCRIPTION}" == "Linux Mint 20"* ]]; then 
#    DISTRO_CODENAME=focal
#fi
#if [[ "${DISTRO_DESCRIPTION}" == "Linux Mint 21"* ]]; then 
#    DISTRO_CODENAME=jammy
#fi

# Build configuration
BUILD_CONFIG=Release
INSTALL_PATH=$PWD/install
CONDUIT_PREFIX=${CONDUIT_PREFIX:-/Users/matthieu/Devs/opt}

pushd ${DIR}
git submodule update --init

GIT_COMMIT_HASH=$(git rev-parse --verify HEAD)

popd

conan profile new autodetect --detect --force
conan install ${DIR} -s compiler.libcxx=libc++ --build missing -g cmake_find_package -g cmake_paths -pr autodetect

cmake ${DIR} \
  -DCMAKE_BUILD_TYPE=${BUILD_CONFIG}\
  -DCMAKE_PREFIX_PATH="${QT_DIR}" \
  -DGIT_COMMIT_HASH=${GIT_COMMIT_HASH} \
  -DCMAKE_INSTALL_PREFIX=${INSTALL_PATH} \
  -DCMAKE_PREFIX_PATH=${CONDUIT_PREFIX}/lib/cmake \
  $@
#  -DCMAKE_MODULE_PATH="${PWD}" \

echo "Build Information:"
echo "  GIT_COMMIT_HASH : ${GIT_COMMIT_HASH}"
#echo "  DISTRO          : ${DISTRO_CODENAME}"


