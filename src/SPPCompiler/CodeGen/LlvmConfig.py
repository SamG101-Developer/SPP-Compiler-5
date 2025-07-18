import ctypes


class LlvmConfig:
    LLVM_MEM_ALIGNMENT = ctypes.sizeof(ctypes.c_void_p)
    LLVM_USIZE         = ctypes.sizeof(ctypes.c_size_t)
