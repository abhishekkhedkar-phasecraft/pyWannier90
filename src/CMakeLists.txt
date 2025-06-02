cmake_minimum_required(VERSION 3.15)
project(pyWannier90)

# Enable Fortran (essential for linking Wannier90)
enable_language(Fortran)

# Find Python and pybind11
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)
find_package(pybind11 REQUIRED)

# Find BLAS and LAPACK (required by Wannier90)
find_package(BLAS REQUIRED)
find_package(LAPACK REQUIRED)

# Set Wannier90 paths - UPDATE THESE TO YOUR INSTALLATION
set(WANNIER90_ROOT "${CMAKE_SOURCE_DIR}/wannier90-3.1.0" 
    CACHE PATH "Path to Wannier90 installation")

# Find Wannier90 library
find_library(WANNIER90_LIBRARY
    NAMES wannier libwannier libwannier90
    PATHS ${WANNIER90_ROOT}
    NO_DEFAULT_PATH
    REQUIRED
)

# Create the extension module
pybind11_add_module(libwannier90
    src/pyWannier90.cpp
    # Add your other source files here
)

# Link libraries in correct order
target_link_libraries(libwannier90 PRIVATE
    ${WANNIER90_LIBRARY}
    ${LAPACK_LIBRARIES}
    ${BLAS_LIBRARIES}
)

# Add Fortran runtime (critical for mixed C++/Fortran)
if(CMAKE_Fortran_COMPILER_ID STREQUAL "GNU")
    target_link_libraries(libwannier90 PRIVATE gfortran)
elseif(CMAKE_Fortran_COMPILER_ID STREQUAL "Intel")
    target_link_libraries(libwannier90 PRIVATE ifcore ifport)
endif()

# Install
install(TARGETS libwannier90 DESTINATION .)

