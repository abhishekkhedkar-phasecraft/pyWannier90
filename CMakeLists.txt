# CMakeLists.txt for pyWannier90
cmake_minimum_required(VERSION 3.15)

project(pyWannier90 
    VERSION 1.0.0
    DESCRIPTION "A Python interface for wannier90"
    LANGUAGES CXX Fortran
)

# Set C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Set Fortran standard  
set(CMAKE_Fortran_STANDARD 95)

# Enable position-independent code for shared libraries
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# Find required packages
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

# Find BLAS and LAPACK with proper fallbacks
find_package(PkgConfig QUIET)

# Try to find BLAS/LAPACK via pkg-config first (preferred)
if(PKG_CONFIG_FOUND)
    pkg_check_modules(BLAS QUIET blas)
    pkg_check_modules(LAPACK QUIET lapack)
endif()

# Fallback to CMake's built-in FindBLAS/FindLAPACK
if(NOT BLAS_FOUND)
    find_package(BLAS REQUIRED)
endif()

if(NOT LAPACK_FOUND)
    find_package(LAPACK REQUIRED)
endif()

# Find Wannier90 library
find_library(WANNIER90_LIBRARY
    NAMES wannier libwannier wannier90 libwannier90
    HINTS
        ${WANNIER90_ROOT}/lib
        ${WANNIER90_ROOT}
        ENV WANNIER90_ROOT
        /usr/local/lib
        /opt/local/lib
        /usr/lib
    DOC "Wannier90 library"
)

if(NOT WANNIER90_LIBRARY)
    message(FATAL_ERROR 
        "Wannier90 library not found. Please set WANNIER90_ROOT or install wannier90 development package")
endif()

# Find Wannier90 headers
find_path(WANNIER90_INCLUDE_DIR
    NAMES wannier_lib.mod w90_constants.mod
    HINTS
        ${WANNIER90_ROOT}/include
        ${WANNIER90_ROOT}/src
        ${WANNIER90_ROOT}
        ENV WANNIER90_ROOT
        /usr/local/include/wannier90
        /opt/local/include/wannier90
        /usr/include/wannier90
    DOC "Wannier90 module directory"
)

if(NOT WANNIER90_INCLUDE_DIR)
    message(FATAL_ERROR 
        "Wannier90 headers/modules not found. Please set WANNIER90_ROOT")
endif()

message(STATUS "Found Wannier90 library: ${WANNIER90_LIBRARY}")
message(STATUS "Found Wannier90 includes: ${WANNIER90_INCLUDE_DIR}")

# Configure compiler-specific flags
if(CMAKE_Fortran_COMPILER_ID MATCHES "GNU")
    set(FORTRAN_FLAGS "-O3 -fPIC -ffast-math")
    add_compile_definitions(gfortran)
elseif(CMAKE_Fortran_COMPILER_ID MATCHES "Intel")
    set(FORTRAN_FLAGS "-O3 -fPIC -xHost")
    add_compile_definitions(ifort)
endif()

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
    set(CXX_FLAGS "-O3 -Wall -fPIC -ffast-math")
elseif(CMAKE_CXX_COMPILER_ID MATCHES "Intel")
    set(CXX_FLAGS "-O3 -fPIC -xHost")
elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    set(CXX_FLAGS "-O3 -Wall -fPIC")
endif()

# Create the Fortran library
add_library(wannier_fortran_lib STATIC
    src/wannier_lib.F90
)

target_include_directories(wannier_fortran_lib PUBLIC
    ${WANNIER90_INCLUDE_DIR}
)

target_compile_options(wannier_fortran_lib PRIVATE
    ${FORTRAN_FLAGS}
)

# Create the Python extension module
pybind11_add_module(libwannier90 
    src/libwannier90.cpp
)

target_include_directories(libwannier90 PRIVATE
    ${WANNIER90_INCLUDE_DIR}
)

target_compile_options(libwannier90 PRIVATE
    ${CXX_FLAGS}
)

# Link libraries with proper RPATH handling
target_link_libraries(libwannier90 PRIVATE
    wannier_fortran_lib
    ${WANNIER90_LIBRARY}
)

# Link BLAS/LAPACK
if(BLAS_FOUND AND BLAS_LIBRARIES)
    target_link_libraries(libwannier90 PRIVATE ${BLAS_LIBRARIES})
    if(BLAS_INCLUDE_DIRS)
        target_include_directories(libwannier90 PRIVATE ${BLAS_INCLUDE_DIRS})
    endif()
endif()

if(LAPACK_FOUND AND LAPACK_LIBRARIES)
    target_link_libraries(libwannier90 PRIVATE ${LAPACK_LIBRARIES})
    if(LAPACK_INCLUDE_DIRS)
        target_include_directories(libwannier90 PRIVATE ${LAPACK_INCLUDE_DIRS})
    endif()
endif()

# Set RPATH for proper runtime library discovery
if(APPLE)
    set_target_properties(libwannier90 PROPERTIES
        INSTALL_RPATH "@loader_path;@loader_path/../lib"
        BUILD_WITH_INSTALL_RPATH TRUE
    )
elseif(UNIX)
    set_target_properties(libwannier90 PROPERTIES
        INSTALL_RPATH "$ORIGIN:$ORIGIN/../lib"
        BUILD_WITH_INSTALL_RPATH TRUE
    )
endif()

# Enable RPATH for build and install trees
set(CMAKE_SKIP_BUILD_RPATH FALSE)
set(CMAKE_BUILD_WITH_INSTALL_RPATH FALSE)
set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)

# Add library directories to RPATH
get_target_property(WANNIER90_LIB_DIR ${WANNIER90_LIBRARY} LOCATION)
get_filename_component(WANNIER90_LIB_DIR ${WANNIER90_LIB_DIR} DIRECTORY)
list(APPEND CMAKE_INSTALL_RPATH ${WANNIER90_LIB_DIR})

if(BLAS_LIBRARIES)
    foreach(lib ${BLAS_LIBRARIES})
        if(EXISTS ${lib})
            get_filename_component(lib_dir ${lib} DIRECTORY)
            list(APPEND CMAKE_INSTALL_RPATH ${lib_dir})
        endif()
    endforeach()
endif()

if(LAPACK_LIBRARIES)
    foreach(lib ${LAPACK_LIBRARIES})
        if(EXISTS ${lib})
            get_filename_component(lib_dir ${lib} DIRECTORY)
            list(APPEND CMAKE_INSTALL_RPATH ${lib_dir})
        endif()
    endforeach()
endif()

# Remove duplicates from RPATH
list(REMOVE_DUPLICATES CMAKE_INSTALL_RPATH)
set_target_properties(libwannier90 PROPERTIES INSTALL_RPATH "${CMAKE_INSTALL_RPATH}")

# Compiler and target information
message(STATUS "C++ Compiler: ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "Fortran Compiler: ${CMAKE_Fortran_COMPILER_ID} ${CMAKE_Fortran_COMPILER_VERSION}")
message(STATUS "BLAS Libraries: ${BLAS_LIBRARIES}")
message(STATUS "LAPACK Libraries: ${LAPACK_LIBRARIES}")
message(STATUS "Install RPATH: ${CMAKE_INSTALL_RPATH}")

# Install the Python module
install(TARGETS libwannier90 DESTINATION .)

# Print configuration summary
message(STATUS "=== pyWannier90 Configuration Summary ===")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Fortran Standard: ${CMAKE_Fortran_STANDARD}")
message(STATUS "Position Independent Code: ${CMAKE_POSITION_INDEPENDENT_CODE}")
message(STATUS "Python: ${Python_EXECUTABLE}")
message(STATUS "===========================================")
