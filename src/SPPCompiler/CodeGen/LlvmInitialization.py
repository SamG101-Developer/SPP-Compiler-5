from llvmlite import binding as llvm


def initialize_llvm() -> None:
    """
    Initialize the LLVM JIT and native target.
    """

    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()
