include("D:/Projects/DeepBule/shixun3QT/build/Desktop_Qt_6_10_1_MinGW_64_bit-Debug/.qt/QtDeploySupport.cmake")
include("${CMAKE_CURRENT_LIST_DIR}/shixun3QT-plugins.cmake" OPTIONAL)
set(__QT_DEPLOY_I18N_CATALOGS "qtbase")

qt6_deploy_runtime_dependencies(
    EXECUTABLE "D:/Projects/DeepBule/shixun3QT/build/Desktop_Qt_6_10_1_MinGW_64_bit-Debug/shixun3QT.exe"
    GENERATE_QT_CONF
)
