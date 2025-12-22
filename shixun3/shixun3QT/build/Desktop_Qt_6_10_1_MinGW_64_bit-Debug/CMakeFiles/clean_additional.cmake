# Additional clean files
cmake_minimum_required(VERSION 3.16)

if("${CONFIG}" STREQUAL "" OR "${CONFIG}" STREQUAL "Debug")
  file(REMOVE_RECURSE
  "CMakeFiles\\shixun3QT_autogen.dir\\AutogenUsed.txt"
  "CMakeFiles\\shixun3QT_autogen.dir\\ParseCache.txt"
  "shixun3QT_autogen"
  )
endif()
