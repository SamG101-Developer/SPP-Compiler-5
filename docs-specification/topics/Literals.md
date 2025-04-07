# Literals

<primary-label ref="header-label"/>

<secondary-label ref="doc-complete"/>

## String Literal

<secondary-label ref="doc-sect-complete"/>

<secondary-label ref="feature-impl"/>

S++ only has one type of string, the `std::Str` type. It is a sequence of characters enclosed in double quotes. The
following escape sequences are supported: `\\`, `\"`, `\n`, `\r`, `\t`. There is no "internal" or "raw" string type,
like Rust's `&str` or C++'s `const char*`.

```
let x = "Hello, world!";
let y = "This is a string with a newline\ncharacter.";
let z = "This is a string with a tab\tcharacter.";
```

All 3 of these variables are of type `std::Str`. Using the `std::Str()` object initialization syntax is equivalent to
`""`. The `std::Str` initializer does not accept a double-quote enclosed string, as it is unnecessary; the double quotes
create a `std::Str` object.

## Number Literal

<secondary-label ref="doc-sect-complete"/>

<secondary-label ref="feature-impl"/>

S++ has 3 different numeric literals: binary, decimal and hexadecimal. Binary and hexadecimal literals are specified
with the following prefixes:

| Literal Type | Prefix | Example  |
|--------------|--------|----------|
| Binary       | `0b`   | `0b1010` |
| Hexadecimal  | `0x`   | `0x2A`   |

Decimal literals can be integers or floats, and can be prefixed with `-` or `+` to indicate their sign. By default, all
numeric literals create either the `BigInt` or `BigDec` types, analogous to Python's `int` and `Decimal` types. This
allows for resource-bound infinite precision arithmetic.

The type of the integer or float can be manually specified with a postfix literal, This is one of 24 types, ranging from
`std::U8` to `std::F256`. The full list of postfix literals is:

| Postfix | Type        | Description              |
|---------|-------------|--------------------------|
| `_u8`   | `std::U8`   | Unsigned 8-bit integer   |
| `_u16`  | `std::U16`  | Unsigned 16-bit integer  |
| `_u32`  | `std::U32`  | Unsigned 32-bit integer  |
| `_u64`  | `std::U64`  | Unsigned 64-bit integer  |
| `_u128` | `std::U128` | Unsigned 128-bit integer |
| `_u256` | `std::U256` | Unsigned 256-bit integer |
| `_i8`   | `std::I8`   | Signed 8-bit integer     |
| `_i16`  | `std::I16`  | Signed 16-bit integer    |
| `_i32`  | `std::I32`  | Signed 32-bit integer    |
| `_i64`  | `std::I64`  | Signed 64-bit integer    |
| `_i128` | `std::I128` | Signed 128-bit integer   |
| `_i256` | `std::I256` | Signed 256-bit integer   |
| `_f8`   | `std::F8`   | Signed 8-bit float       |
| `_f16`  | `std::F16`  | Signed 16-bit float      |
| `_f32`  | `std::F32`  | Signed 32-bit float      |
| `_f64`  | `std::F64`  | Signed 64-bit float      |
| `_f128` | `std::F128` | Signed 128-bit float     |
| `_f256` | `std::F256` | Signed 256-bit float     |

Any of these types, as well as the big number types, can be called as regular object initializers, and will default to
`0`.

## Boolean Literal

<secondary-label ref="doc-sect-complete"/>

<secondary-label ref="feature-impl"/>

There are two keywords for boolean literals in S++: `true` and `false`. These are the only two boolean literals in S++,
and are used to represent the `std::Bool` type. The `std::Bool` initializer can be called, and will default the value to
`False`.

## Array Literal

<secondary-label ref="doc-sect-complete"/>

<secondary-label ref="feature-impl"/>

The array literal is a list of same-type items inside the `[]` tokens. The type of the array, and its size, are inferred
from the items. For example, `let x = [1, 2, 3]` infers a `std::Arr[std::BigNum, 3]` type. Note that the size of an
array is fixed, so it might be necessary to use the `std::Vec` type if the size is unknown.

## Tuple Literal

<secondary-label ref="doc-sect-complete"/>

<secondary-label ref="feature-impl"/>

The tuple literal is a list of different-type items inside the `()` tokens. The type of the tuple is inferred from the
items. For example, `let x = (1, "Hello", 3.14)` infers a `std::Tup[std::BigNum, std::Str, std::BigDec]` type. There is
slightly different syntax for 1-tuples, to differentiate them from regular parenthesized expressions.

| Tuple Length | Syntax   | Example  |
|--------------|----------|----------|
| 0            | `()`     | `()`     |
| 1            | `(x,)`   | `(1,)`   |
| 2            | `(x, y)` | `(1, 2)` |
