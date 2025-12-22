include("D:/Projects/DeepBule/DeepBlueOpenCV/shixun3/shixun3QT/out/build/x64-Debug/.qt/QtDeploySupport.cmake")
include("${CMAKE_CURRENT_LIST_DIR}/shixun3QT-plugins.cmake" OPTIONAL)
set(__QT_DEPLOY_I18N_CATALOGS "qtbase")

qt6_deploy_runtime_dependencies(
    EXECUTABLE "D:/Projects/DeepBule/DeepBlueOpenCV/shixun3/shixun3QT/out/build/x64-Debug/shixun3QT.exe"
    GENERATE_QT_CONF
)
