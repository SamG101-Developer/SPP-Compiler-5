# Basic Types

S++ has a number of basic types, which are the building blocks of all S++ programs. This section will detail the basic
types in S++. The basic types in S++ are:

- [Number types](#number-types)
- [Boolean type](#boolean-type)
- [Void type](#void-type)

As every type in S++ is treated as first class, these types are also treated as objects, and follow standard type
identifier regex, rather that a keyword-like identifier. All of these types have `std::copy::Copy` superimposed over
them, to allow easy use of the numbers without having to place `.clone()` everywhere for simple calculations.

## Number Types

S++ uses a large range of numeric types, allowing for low-level optimizations and refined resource utilization on
embedded devices. The naming convention is inspired by Rust, but modified to match the syntactic type-identifier
requirements.

All of these types are found in the `std::number` module of the STL:

| Type     | Postfix | Size (bits) | Min           | Max          | Precision  | Description                 |
|----------|---------|-------------|---------------|--------------|------------|-----------------------------|
| `U8`     | `_u8`   | `8`         | `0`           | `2^8 - 1`    | `8 bits`   | Unsigned 8-bit integer      |
| `U16`    | `_u16`  | `16`        | `0`           | `2^16 - 1`   | `16 bits`  | Unsigned 16-bit integer     |
| `U32`    | `_u32`  | `32`        | `0`           | `2^32 - 1`   | `32 bits`  | Unsigned 32-bit integer     |
| `U64`    | `_u64`  | `64`        | `0`           | `2^64 - 1`   | `64 bits`  | Unsigned 64-bit integer     |
| `U128`   | `_u128` | `128`       | `0`           | `2^128 - 1`  | `128 bits` | Unsigned 128-bit integer    |
| `U256`   | `_u256` | `256`       | `0`           | `2^256 - 1`  | `256 bits` | Unsigned 256-bit integer    |
| `I8`     | `_i8`   | `8`         | `-2^7`        | `2^7 - 1`    | `7 bits`   | Signed 8-bit integer        |
| `I16`    | `_i16`  | `16`        | `-2^15`       | `2^15 - 1`   | `15 bits`  | Signed 16-bit integer       |
| `I32`    | `_i32`  | `32`        | `-2^31`       | `2^31 - 1`   | `31 bits`  | Signed 32-bit integer       |
| `I64`    | `_i64`  | `64`        | `-2^63`       | `2^63 - 1`   | `63 bits`  | Signed 64-bit integer       |
| `I128`   | `_i128` | `128`       | `-2^127`      | `2^127-1`    | `127 bits` | Signed 128-bit integer      |
| `I256`   | `_i256` | `256`       | `-2^255`      | `2^255-1`    | `255 bits` | Signed 256-bit integer      |
| `F8`     | `_f8`   | `8`         | `~ -2^7`      | `~ 2^7`      | `e4m3`     | Signed 8-bit float          |
| `F16`    | `_f16`  | `16`        | `~ -2^15`     | `~ 2^15`     | `e5m10`    | Signed 16-bit float         |
| `F32`    | `_f32`  | `32`        | `~ -2^127`    | `~ 2^127`    | `e8m23`    | Signed 32-bit float         |
| `F64`    | `_f64`  | `64`        | `~ -2^1023`   | `~ 2^1023`   | `e11m52`   | Signed 64-bit float         |
| `F128`   | `_f128` | `128`       | `~ -2^16383`  | `~ 2^16383`  | `e15m112`  | Signed 128-bit float        |
| `F256`   | `_f256` | `256`       | `~ -2^262143` | `~ 2^262143` | `e18m237`  | Signed 256-bit float        |
| `BigInt` | `N/A`   | `inf`       | `-inf`        | `inf`        | `inf`      | Arbitrary precision integer |
| `BigDec` | `N/A`   | `inf`       | `-inf`        | `inf`        | `inf`      | Arbitrary precision float   |

A number literal's is always the `std::number::BigInt` or `std::number::BigDec` if no postfix type is provided. Use the
above postfixes to set the numeric type explicitly. All the number types, except `BigInt` and `BigDec` have compiler
builtin operation methods, to hook into llvm-specialized functions.

The `Copy` class is superimposed over all of these number types so that they can be used in calculations easily without
having to manually clone them. Also, numer types are small so this doesnt create a memory issue.

## Boolean Type

The boolean type is S++ is `std::boolean::Bool`. This is a compiler known type that maps to the llvm `bool` type.
Literals `true`and `false` are used to create boolean value types. The `Copy` class is superimposed over the boolean
type as-well.

## Void Type

The void type in S++ is `Void`. This is a compiler known type that maps to the llvm `void` type. The `Void` type is used
to represent the absence of a value, and is used as the return type for functions that do not return a value. Variables
cannot hold a `Void` type, and function parameters whose type is generic (and the generic argument is `Void`), are
removed from the substituted signature.
