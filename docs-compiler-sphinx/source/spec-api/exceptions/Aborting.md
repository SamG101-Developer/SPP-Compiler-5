## Aborting

Sometimes, an unrecoverable error occurs during the runtime execution of a program. In such cases, the program must
abort, and the compiler must ensure that the program does not continue executing in an invalid state. This is done by
using the `std::abort::abort` method, which is a built-in function that terminates the program immediately. It returns
the `!` never type, indicating that once this function is called it will never return.

A `Str` message can be passed into the `std::abort::abort` method, which will be printed to the standard error output
with the stack trace of the program at the point of the abort. This is useful for debugging purposes, as it allows the
developer to see where the program was when it aborted, and what the error message was. The `std::abort::abort` method
can be called from anywhere in the program, and it will immediately terminate the program, regardless of where it is
called from.
