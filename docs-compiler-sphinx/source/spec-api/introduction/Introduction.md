# Introduction

S++ is a modern, general-purpose systems programming language, inheriting the syntax of a Rust-Python fusion. It is
strongly and statically typed, and has a specific focus on memory safety, runtime performance, and ease of use. There
are a number of features in S++ that make it a powerful language for systems programming, such as: full type inference,
pattern matching, generics, modules and coroutines.

S++ aims to be completely memory-safe, type-safe, and thread-safe, while providing the performance of a low-level
language, with no bizarre syntax or complex rules. A blend of techniques is used to enforce memory safety, including
second-class borrows, the law of exclusivity, and ownership tracking.

## Philosophy

- **Performance**: S++ is designed as a high-performance language, achieved by compiling S++ code to native code, using
  an LLVM backend. This allows S++ to have performance statistics comparable to C++ and Rust.
- **Readability**: S++ is designed to be simple to read, with a left-to-right, top-to-bottom reading rule for every
  block of code. Whilst loosely based on the C-family syntax, a number of changes were made to remove legacy syntax.
- **Orthogonal**: S++ is designed to be consistent in all aspects. A key example is treating integers, booleans, tuples,
  arrays, variants and functions all as first-class object, with no specific behaviour or context rules for any of
  them.
- **Versatile**: S++ is designed to be a low level language with a high level syntax. This allows it to be used for a
  wide range of applications, from systems programming to desktop applications.
- **Efficient**: User and machine efficiency were considered throughout the design of S++. This includes stripping out
  legacy features, forcing type inference, and maintaining "one correct way to do things".
- **Safety**: S++ enforces memory safety, thread safety, and type safety using a range of features. This allows the high
  performance, low level nature of the language to be used without the risk of crashes or undefined behaviour.

## Key Features

- **Expression Oriented**: In S++, almost every "statement" is an expression, including conditional branching,
  conditional looping, contextual blocks, etc.

- **Advanced Type System**: All types in S++ are first-class. Flow typing, type shorthands, type inference, type
  aliasing, and a full generic system are all supported.
- **Memory Safety**: S++ follows Rust in having a strong emphasis on memory safety. It uses a blend of techniques to
  ensure that memory is managed safely and efficiently, mitigating memory bugs.
- **Class System**: The class system in S++ is split into state and behaviour. Each class definition includes state
  only (attributes). All methods and inheritance are defined using superimposition.
- **Superimposition**: Similar to Rust `impl`, behaviour blocks or isolated type extension blocks with controlled
  override capability.
- **Module System**: Module definitions, namespaces and directory structures are all the same in S++, providing a
  structured and simple module system. All modules are "imported" but namespaced.
- **Functions**: Function and methods support overloading and recursion, and type-afe variadic parameters. Functions
  can be called asynchronously, and closures can capture variables from their enclosing scope.
- **Generics**: S++ has a powerful generics system, supporting generic functions, types and methods. Generic types can
  be constrained. Generic types can also be variadic, allowing for a variable number of type arguments.
- **Asynchronous functions**: S++ uses Golang like syntax for asynchronous functions, where the asynchronous convention
  is defined at the function call site, not the function definition, mitigating the "function color" problem.
- **Concurrency**: Coroutines form the concurrency model in S++. They can be suspended and resumed, support
  bilateral data movement, and can yield borrowed values. They form the basis of iteration.
- **Parallelism**: S++ uses threads, and their associated primitives, such as mutexes and condition variables, for
  parallelism. This is pulled from C++, withAPIs have been modernized to fit S++.
- **Error Handling**: S++ uses a result-type for error handling, similar to Rust. This allows for more expressive
  error handling. The `?` operator cn be used to propagate errors up the call stack.
- **Pattern Matching**: S++ has a powerful pattern matching system. This allows for complex
  destructuring of tuples, arrays, object and variants, and can be used in conjunction with flow typing.
- **Loop Control Flow**. S++ provides the ability to exit or skip an iteration of an n-depth loop. This alsop allows
  variables to be returned out of loops.
  4**Operator Overloading**: S++ supports operator overloading, allowing for operators to be defined for custom types.
