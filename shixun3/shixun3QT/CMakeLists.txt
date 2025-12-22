# 在CMakeLists.txt中，注释使用#，此文件有cmake工具进行处理

# 请求最小的cmake版本(低于此版本的cmake工具，是无法构建这个项目)
cmake_minimum_required(VERSION 3.19)

# 设置项目相关信息
#--shixun3QT 项目名称
#--VERSION 0.1 项目版本
#--LANGUAGES CXX CXX就是C++,表示此项目使用的语言是C++
project(shixun3QT LANGUAGES CXX)

# 查找包
find_package(Qt6 6.5 REQUIRED COMPONENTS Core Widgets)

# set命令是用来设置变量的
qt_standard_project_setup()

# 设置项目使用的文件，只有在这里设置了的文件，才会显示到项目树中
qt_add_executable(shixun3QT
    MACOSX_BUNDLE
    main.cpp
    Widget.cpp
    Widget.h
)

# 目标链接库:指定要链接到可执行程序中的库文件
target_link_libraries(shixun3QT
    PRIVATE
        Qt::Core
        Qt::Widgets
)

include(GNUInstallDirs)

install(TARGETS shixun3QT
    BUNDLE  DESTINATION .
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

qt_generate_deploy_app_script(
    TARGET shixun3QT
    OUTPUT_SCRIPT deploy_script
    NO_UNSUPPORTED_PLATFORM_ERROR
)
install(SCRIPT ${deploy_script})
