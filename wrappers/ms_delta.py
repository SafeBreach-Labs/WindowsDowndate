import ctypes

from wrappers.ms_delta_definitions import ApplyDeltaB, DELTA_INPUT, DELTA_OUTPUT


def apply_delta(delta_file_flag: ctypes.c_int64, source: bytes, delta: bytes) -> DELTA_OUTPUT:
    source_delta_input = DELTA_INPUT()
    source_delta_input.lpStart = ctypes.create_string_buffer(source)
    source_delta_input.uSize = len(source)
    source_delta_input.Editable = False

    delta_delta_input = DELTA_INPUT()
    delta_delta_input.lpStart = ctypes.create_string_buffer(delta)
    delta_delta_input.uSize = len(delta)
    delta_delta_input.Editable = False

    target_delta_output = DELTA_OUTPUT()

    ApplyDeltaB(delta_file_flag, source_delta_input, delta_delta_input, ctypes.byref(target_delta_output))

    return target_delta_output
