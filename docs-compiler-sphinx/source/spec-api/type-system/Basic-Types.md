# Basic Types

<primary-label ref="header-label"/>

<secondary-label ref="doc-complete"/>


S++ has a number of basic types, which are the building blocks of all S++ programs. This section will detail the basic
types in S++. The basic types in S++ are:
- Number types
- Boolean type
- Void type

## Number Types

<secondary-label ref="doc-sect-complete"/>

<secondary-label ref="feature-impl"/>

Number types are mostly inspired by Rust, using the short type names rather than `char, short, int, long, long long`etc.
However, the amount of number types has been extended, to make the language more versatile. The number types in S++ are:

<tabs>
<tab id="U" title="Unsigned Integers">

| Type   | Size (bits) | Min | Max     | Precision | Description              |
|--------|-------------|-----|---------|-----------|--------------------------|
| `U8`   | 8           | 0   | 2^8 - 1 | 8 bits    | Unsigned 8-bit integer   |
| `U16`  | 16          | 0   | 2^16- 1 | 16 bits   | Unsigned 16-bit integer  |
| `U32`  | 32          | 0   | 2^32- 1 | 32 bits   | Unsigned 32-bit integer  |
| `U64`  | 64          | 0   | 2^64- 1 | 64 bits   | Unsigned 64-bit integer  |
| `U128` | 128         | 0   | 2^128-1 | 128 bits  | Unsigned 128-bit integer |
| `U256` | 256         | 0   | 2^256-1 | 256 bits  | Unsigned 256-bit integer |

</tab>
<tab id="I" title="Signed Integers">

| Type   | Size (bits) | Min    | Max      | Precision | Description            |
|--------|-------------|--------|----------|-----------|------------------------|
| `I8`   | 8           | -2^7   | 2^7 - 1  | 7 bits    | Signed 8-bit integer   |
| `I16`  | 16          | -2^15  | 2^15 - 1 | 15 bits   | Signed 16-bit integer  |
| `I32`  | 32          | -2^31  | 2^31 - 1 | 31 bits   | Signed 32-bit integer  |
| `I64`  | 64          | -2^63  | 2^63 - 1 | 63 bits   | Signed 64-bit integer  |
| `I128` | 128         | -2^127 | 2^127-1  | 127 bits  | Signed 128-bit integer |
| `I256` | 256         | -2^255 | 2^255-1  | 255 bits  | Signed 256-bit integer |

</tab>
<tab id="F" title="Floating Points">

| Type   | Size (bits) | Min    | Max      | Precision | Description          |
|--------|-------------|--------|----------|-----------|----------------------|
| `F8`   | 8           | -2^7   | 2^7 - 1  | 7 bits    | Signed 8-bit float   |
| `F16`  | 16          | -2^15  | 2^15 - 1 | 15 bits   | Signed 16-bit float  |
| `F32`  | 32          | -2^31  | 2^31 - 1 | 31 bits   | Signed 32-bit float  |
| `F64`  | 64          | -2^63  | 2^63 - 1 | 63 bits   | Signed 64-bit float  |
| `F128` | 128         | -2^127 | 2^127-1  | 127 bits  | Signed 128-bit float |
| `F256` | 256         | -2^255 | 2^255-1  | 255 bits  | Signed 256-bit float |

</tab>
<tab id="O" title="Other">

| Type     | Size (bits) | Min  | Max | Precision | Description                 |
|----------|-------------|------|-----|-----------|-----------------------------|
| `BigInt` | inf         | -inf | inf | inf       | Arbitrary precision integer |
| `BigDec` | inf         | -inf | inf | inf       | Arbitrary precision float   |

</tab>
</tabs>

A numeric literal without a postfix type specifier will default to the `BigInt` or `BigDec` type, depending on whether
it is an integer or float. All these types are compiler known, and have special behaviour, except from the `BigXYZ`
types. All numbers have the `Copy` class superimposed over them.

## Boolean Type

<secondary-label ref="doc-sect-complete"/>

<secondary-label ref="feature-impl"/>

The boolean type is S++ is `std::Bool`. This is a compiler known type that maps to the llvm `bool` type. Literals `true`
and `false` are used to create boolean value types. The `Copy` class is superimposed over the `std::Bool` type.

## Void Type

<secondary-label ref="doc-sect-complete"/>

<secondary-label ref="feature-impl"/>

The void type in S++ is `Void`. This is a compiler known type that maps to the llvm `void` type. The `Void` type is used
to represent the absence of a value, and is used as the return type for functions that do not return a value. Variables
cannot hold a `Void` type, and function parameters whose type is generic and the generic argument is `Void`, are removed
from the substituted signature.
