cmake_minimum_required(VERSION 3.16)
project(ImageAnnotator)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_AUTOMOC ON)

find_package(Qt6 REQUIRED COMPONENTS Core Gui Quick)

set(SOURCES
    src/main.cpp
    src/ImageProcessor.cpp
)

set(HEADERS
    src/ImageProcessor.h
)

qt_add_executable(${PROJECT_NAME}
    ${SOURCES}
    ${HEADERS}
    resources.qrc
)

target_link_libraries(${PROJECT_NAME} PRIVATE Qt6::Core Qt6::Gui Qt6::Quick)
