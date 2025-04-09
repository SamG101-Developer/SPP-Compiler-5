# STL Structure

<primary-label ref="header-label"/>

<secondary-label ref="doc-wip"/>

## Structure of the Standard Library

The standard library in S++ is split into 3 "layers": the [core](#core-layer), [foundation](#foundation-layer),
and [extended](#extended-layer) layers. The core layer is required even on barebones systems, while the foundation and
extended layers are optional. The foundation layer provides additional functionality, while the extended layer provides
advanced non-crucial functionality, pulling in ffi libraries and other OS-abstracted code.

All `types` mentioned in this section are part of the `std` namespace, and are therefore `std::XYZ` types.

### Core Layer

Every type in the core layer is in the core layer because the compiler itself knows about the type, and is required to
know about it, whether it be for custom memory management, code generation or other reasons. The core layer is the
smallest layer, and is the only layer that is required to be present on all systems.

- `U8`
- `U16`
- `U32`
- `U64`
- `U128`
- `U256`
- `I8`
- `I16`
- `I32`
- `I64`
- `I128`
- `I256`
- `F8`
- `F16`
- `F32`
- `F64`
- `F128`
- `F256`
- `Bool`
- `Void`
- `Copy`
- `Arr[T, n]`
- `Vec[T]`
- `Var[..Types]`
- `Any`
- `FunMov[(Out), Ret]`
- `FunMut[(Out), Ret]`
- `FunRef[(Out), Ret]`
- `GenMov[Gen, Send]`
- `GenMut[Gen, Send]`
- `GenRef[Gen, Send]`
- `IterMov[T]`
- `IterMut[T]`
- `IterRef[T]`
- `Fut[T]`
- `Opt[T]`
- `Box[T]`
- `Vol[T]`
- `Tup[..Types]`
- `CtxMut[Out]`
- `CtxRef[Out]`
- `Atom[T]`

{columns="5"}

### Foundation Layer

Types in the foundation layer are unknown to the compiler, and are not required for the compiler to function. Types in
the foundation layer will be highly optimized withing the constraint of S++, and so are recommended to use for most
applications.

- `Ret[T, E]`
- `Str`
- `Map[K, V]`
- `Set[T]`
- `Queue[T]`
- `Stack[T]`
- `LinkedList[T]`
- `Clone`
- `BigInt`
- `BigDec`
- `Rgx`

{columns="5"}

### Extended Layer

Types in the extended layer are not required for the compiler to function, and are usable for any application. The S++
extended layer's types are mostly OS-wrapped primitives from C libraries, such as threading, io, and sockets. A few
examples of these types are:

- `Thread`
- `Mutex`
- `Socket`
- `File`

{columns="5"}
