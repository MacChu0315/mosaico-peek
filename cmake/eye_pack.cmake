get_filename_component(PEEK_ROOT "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
set(PEEK_EYE_GENERATED_DIR "${CMAKE_BINARY_DIR}/eye-generated")
if(CMAKE_SCRIPT_MODE_FILE)
    return()
endif()
file(MAKE_DIRECTORY "${PEEK_EYE_GENERATED_DIR}")
file(GLOB_RECURSE PEEK_EYE_INPUTS "${PEEK_ROOT}/assets/eye-pack/*" "${PEEK_ROOT}/assets/mechanical-c/*")
add_custom_command(OUTPUT "${PEEK_EYE_GENERATED_DIR}/eye_pack.inc"
    BYPRODUCTS "${PEEK_EYE_GENERATED_DIR}/eye_pack.json"
    COMMAND "${Python3_EXECUTABLE}" "${PEEK_ROOT}/tools/bake_eye_pack.py"
        --output "${PEEK_EYE_GENERATED_DIR}/eye_pack.inc"
    DEPENDS "${PEEK_ROOT}/tools/bake_eye_pack.py" "${PEEK_ROOT}/assets/eye_motion.json" "${PEEK_ROOT}/assets/mechanical-c-adaptation.json" ${PEEK_EYE_INPUTS} VERBATIM)
add_custom_target(peek_eye_assets DEPENDS "${PEEK_EYE_GENERATED_DIR}/eye_pack.inc")
