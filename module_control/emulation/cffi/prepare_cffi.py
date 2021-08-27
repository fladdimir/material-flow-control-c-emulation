# prepares the cffi wrapper layer and the shared objects for the C control code
# which is called as part of the Python emulation environment

import os

import cffi

this_dir = os.path.dirname(__file__)
h_file_name = this_dir + "/../../module.h"

with open(h_file_name) as h_file:
    header_content = h_file.read()

ffi = cffi.FFI()
ffi.cdef(
    """
    extern "Python+C" bool _light_barrier();
    extern "Python+C" bool _endlage_0();
    extern "Python+C" bool _endlage_90();
    extern "Python+C" void _set_rotation(int dir);
    extern "Python+C" void _set_translation(int dir);
    extern "Python+C" long _millis();
    extern "Python+C" int _serial_read(); // byte or -1 if nothing to read
    extern "Python+C" void _serial_write(int b);
    extern "Python+C" void _log(char *message);
    extern "Python+C" void _throw_exception();
    """
    + header_content
)

ffi.set_source(
    "module_control.emulation.cffi.cffi_module",
    '#include "../../module.h"',
    sources=["module_control/module.c"],
)

ffi.compile(verbose=False)
