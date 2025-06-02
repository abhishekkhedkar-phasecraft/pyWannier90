# Fixed CMakeLists.txt for pyWannier90
# This version implements proper dependency discovery and RPATH configuration

cmake_minimum_required(VERSION 3.15...3.30)
project(${SKBUILD_PROJECT_NAME} LANGUAGES CXX Fortran)

# Set C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Position independent code for shared libraries
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Find Python
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

# Find pybind11
find_package(pybind11 CONFIG REQUIRED)

# Find BLAS and LAPACK using modern CMake
find_package(PkgConfig QUIET)
if(PKG_CONFIG_FOUND)
    pkg_check_modules(BLAS blas)
    pkg_check_modules(LAPACK lapack)
endif()

# Fallback to CMake's built-in finders if pkg-config fails
if(NOT BLAS_FOUND)
    find_package(BLAS REQUIRED)
endif()
if(NOT LAPACK_FOUND)
    find_package(LAPACK REQUIRED)
endif()

# Try to find Wannier90 library
find_library(WANNIER90_LIB
    NAMES wannier90 libwannier90
    HINTS 
        $ENV{WANNIER90_ROOT}/lib
        $ENV{WANNIER90_ROOT}/build
        /usr/local/lib
        /opt/homebrew/lib
    DOC "Wannier90 library"
)

find_path(WANNIER90_INCLUDE
    NAMES wannier90.h
    HINTS
        $ENV{WANNIER90_ROOT}/include
        $ENV{WANNIER90_ROOT}/src
        /usr/local/include
        /opt/homebrew/include
    DOC "Wannier90 include directory"
)

if(WANNIER90_LIB AND WANNIER90_INCLUDE)
    message(STATUS "Found Wannier90: ${WANNIER90_LIB}")
    set(WANNIER90_FOUND TRUE)
else()
    message(STATUS "Wannier90 not found, will build without it")
    set(WANNIER90_FOUND FALSE)
endif()

# Create the pybind11 module
pybind11_add_module(libwannier90 MODULE libwannier90.cpp)

# Add include directories
if(WANNIER90_FOUND)
    target_include_directories(libwannier90 PRIVATE ${WANNIER90_INCLUDE})
endif()

# Link required libraries
target_link_libraries(libwannier90 PRIVATE ${BLAS_LIBRARIES} ${LAPACK_LIBRARIES})

if(WANNIER90_FOUND)
    target_link_libraries(libwannier90 PRIVATE ${WANNIER90_LIB})
endif()

# Platform-specific linking flags
if(APPLE)
    target_link_options(libwannier90 PRIVATE "-undefined" "dynamic_lookup")
endif()

# Set RPATH for the Python module
set_target_properties(libwannier90 PROPERTIES
    INSTALL_RPATH_USE_LINK_PATH TRUE
)

if(APPLE)
    set_target_properties(libwannier90 PROPERTIES
        INSTALL_RPATH "@loader_path;@loader_path/../lib"
        MACOSX_RPATH TRUE
    )
elseif(UNIX)
    set_target_properties(libwannier90 PROPERTIES
        INSTALL_RPATH "$ORIGIN:$ORIGIN/../lib"
    )
endif()

# Install targets
install(TARGETS libwannier90 
	    LIBRARY DESTINATION ${SKBUILD_PROJECT_NAME}
	    )

# Print configuration summary
message(STATUS "=== pyWannier90 Build Configuration ===")
message(STATUS "Python version: ${Python_VERSION}")
message(STATUS "BLAS libraries: ${BLAS_LIBRARIES}")
message(STATUS "LAPACK libraries: ${LAPACK_LIBRARIES}")
if(WANNIER90_FOUND)
    message(STATUS "Wannier90 library: ${WANNIER90_LIB}")
    message(STATUS "Wannier90 include: ${WANNIER90_INCLUDE}")
else()
    message(STATUS "Wannier90: Not found")
endif()
message(STATUS "Install RPATH: Enabled")
message(STATUS "=======================================")

