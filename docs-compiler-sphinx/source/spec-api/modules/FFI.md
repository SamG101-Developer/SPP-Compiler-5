# 13.2. FFI

## Foreign Function Interface

S++ can interface will other language that create object or library files, and conform to the `C` ABI. The `ffi` folder
must be present in the project root, and contain subfolders for each library that is being interfaced with.

For example, if the project is interfacing with the `v8` library, then the `ffi` folder must contain a `v8` subfolder.
This subfolder will then contain the shared object file for the library, as well as a `stub.spp` file that contains the
function signatures for the functions that are being called.

The `ffi` folder might look like:

```
ffi
├── v8
│   ├── libv8.so
│   ├── libv8.dylib
│   ├── libv8.dll
│   └── stub.spp
└── libuv
    ├── libuv.so
    ├── libuv.dylib
    ├── libuv.dll
    └── stub.spp
```

## C++ Interfacing

Here are the steps involved to interface a `C++` library with `S++`:

1. **Create the C++ library:** Define the functions you want to expose to S++. They must be declared as `extern "C"` to
   prevent name mangling, so that the mapping between S++ and C++ function names is straightforward.
2. **Compile the C++ library:** The target output must be a shared object file (`.so` on Linux, `.dll` on
   Windows, `.dylib` on macOS). This will combine all the relevant object files into 1 library.
3. **Make the library accessible to S++:** Move the shared object into the `ffi/library_name` directory of your S++
   project. Dependency libraries must also be moved into their respective directories. (Tool provided for this).
4. **Create a stub file:** This file will contain the function signatures of the functions you want to call from S++,
   and the class definitions of any objects you want to create in S++. The stub file must be named `stub.spp`, and must
   reside in the `ffi/library_name` directory
5. **Use the functions in S++:** Call the functions from S++ as if they were native functions. They will be namespaced
   under the standard 3rd party section, just as other `vcs` loaded modules would be: `use ffi::library_name::*`.
   The `ffi` namespace is reserved for external libraries, and the `library_name` namespace is the name of the shared
   object file.

### Example (general) {collapsible="true"}

#### C++ Code

```c++
// add.cpp
extern "C" __declspec(dllexport) int add(int a, int b) {
    return a + b;
}


// sub.cpp
extern "C" __declspec(dllexport) int sub(int a, int b) {
    return a - b;
}
```

#### Compile all files into a shared object file

```bash
g++ -shared -o lib_math.dll add.cpp sub.cpp
mv lib_math.dll {ProjectPath}/ffi/lib_math
```

#### S++ Stub Code

```
# ffi/lib_math/stub.spp
fun add(a: I32, b: I32) -> I32 { }
fun sub(a: I32, b: I32) -> I32 { }
```

#### S++ Code

```
use ffi::example::{add, sub};

fun main() -> Void {
    let a = add(1_u32, 2_u32)  # U32
    let b = sub(3_u32, 4_u32)  # U32
}
```

## Conversions

As all languages available to the ffi must conform to the `C` ABI, it is known that all functions will have been
exported using `extern "C"` or something similar. This means only a type-mapping between `S++` and `C` ABI types is
needed. The following table shows the conversions that are made when calling a `C` ABI function from S++:

| C Type               | S++ Type | Notes                        |
|----------------------|----------|------------------------------|
| `char`               | `I8`     | Identical types, no change   |
| `short`              | `I16`    | Identical types, no change   |
| `int`                | `I32`    | Identical types, no change   |
| `long`               | `I64`    | Identical types, no change   |
| `long long`          | `I64`    | Identical types, no change   |
| `unsigned char`      | `U8`     | Identical types, no change   |
| `unsigned short`     | `U16`    | Identical types, no change   |
| `unsigned int`       | `U32`    | Identical types, no change   |
| `unsigned long`      | `U64`    | Identical types, no change   |
| `unsigned long long` | `U64`    | Identical types, no change   |
| `float`              | `F32`    | Identical types, no change   |
| `double`             | `F64`    | Identical types, no change   |
| `long double`        | `F64`    | Identical types, no change   |
| `bool`               | `Bool`   | Identical types, no change   |
| `void`               | `Void`   | Identical types, no change   |
| `T*`                 | `&mut T` | Only as a function parameter |
| `const T*`           | `&T`     | Only as a function parameter |
| `T[]`                | `Arr[T]` | ?                            |

### Important notes

1. The other S++ primitives (`I128`, `I256`, `U128`, `U256`, `F8`, `F16`, `F128`, `F256`) do not have direct C
   equivalents, and so cannot be used in FFI calls.
2. Not all features of every language will be supported. For example, C++ templates are not supported, and so cannot be
   used in FFI calls, until a template <-> generics conversion is implemented.
3. Other languages classes and constructors aren't supported by S++ as object initialization is done in S++ itself.
   Again, as the system is further developed, this may change.
4. C++ functions returning pointers cannot be interfaced into S++, as S++ does not allow borrows as return values,
   enforcing second class borrows. Instead, the smart pointer `Single[T]` is returned, as this represents a value on the
   heap.

## Safety

S++ does not have a concept of pointers, and so cannot directly access memory. This means that the FFI is inherently
safe, as it cannot cause memory corruption or leaks. However, the C++ functions can still cause undefined behaviour if
they are not written correctly.

As such, all FFI code, no matter the language, is executed in isolated stacks, with every function call's return value
being wrapped in the result `Res[Pass, Fail]` type. This means that if the function call fails, then the error will be
propagated up the call stack, and the program will not crash.

## Exporting S++ Functions

S++ functions can be exported to other languages, but only if the functions are public and follow the `C` ABI. This is
done by using the `@public` and  `@repr_c` annotation, (with the argument being the "C" convention):

```
@public
@repr_c
fun add(a: I32, b: I32) -> I32 {
    ret a + b
}
```

This encourages a design where a separate `@repr_c` API is created, which calls the internal S++ functions. This allows
the internal functions to be changed without affecting the external API, and also makes the API safer by isolating the
FFI code from the rest of the program.

## Design Decisions

1. The reason for having **subfolders within the `ffi` folder** is that shared objects for different platforms can be
   placed in the same folder, and the correct one will be chosen during compilation. It also assists with dependency
   management.