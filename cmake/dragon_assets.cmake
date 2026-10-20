# Ordinary builds validate retained sources and write only in the build tree.
get_filename_component(PEEK_ROOT "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
set(PEEK_GENERATED_DIR "${CMAKE_BINARY_DIR}/dragon-generated")
set(PEEK_ASSETS_INC "${PEEK_GENERATED_DIR}/dragon_assets.inc")
# IDF first scans component dependencies in CMake script mode; no targets exist.
if(CMAKE_SCRIPT_MODE_FILE)
    return()
endif()
if(DEFINED ENV{PEEK_ASSET_PYTHON})
    set(Python3_EXECUTABLE "$ENV{PEEK_ASSET_PYTHON}")
endif()
if(NOT Python3_EXECUTABLE)
    find_package(Python3 REQUIRED COMPONENTS Interpreter)
endif()
set(PEEK_GENERATED_DIR "${CMAKE_BINARY_DIR}/dragon-generated")
set(PEEK_ASSETS_INC "${PEEK_GENERATED_DIR}/dragon_assets.inc")
file(MAKE_DIRECTORY "${PEEK_GENERATED_DIR}")
add_custom_command(OUTPUT "${PEEK_ASSETS_INC}"
    BYPRODUCTS "${PEEK_GENERATED_DIR}/dragon_assets.generation.json"
    COMMAND "${CMAKE_COMMAND}" -E make_directory "${PEEK_GENERATED_DIR}"
    COMMAND "${Python3_EXECUTABLE}" "${PEEK_ROOT}/tools/bake_dragon.py" --output "${PEEK_ASSETS_INC}"
    DEPENDS "${PEEK_ROOT}/tools/bake_dragon.py" "${PEEK_ROOT}/assets/dragon/skin.png" "${PEEK_ROOT}/assets/dragon/iris.png"
            "${PEEK_ROOT}/assets/dragon/metadata.json"
    VERBATIM)
add_custom_target(peek_dragon_assets DEPENDS "${PEEK_ASSETS_INC}")
