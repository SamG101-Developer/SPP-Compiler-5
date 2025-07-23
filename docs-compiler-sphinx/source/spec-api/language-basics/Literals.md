# Literals

## String Literal

S++ only has one type of string, the `std::string::Str` type. It is a sequence of characters enclosed in double quotes.
The following escape sequences are supported: `\\`, `\"`, `\n`, `\r`, `\t`. There is no "internal" or "raw" string type,
like Rust's `&str` or C++'s `const char*`.

```S++
let x = "Hello, world!"
let y = "This is a string with a newline\ncharacter."
let z = "This is a string with a tab\tcharacter."
```

All 3 of these variables are of type `std::string::Str`. Using the `std::string::Str()` object initialization syntax is
equivalent to `""`. The `std::string::Str` initializer does not accept a double-quote enclosed string, as it is
unnecessary; the double quotes create a `std::string::Str` object already.

## Number Literal

S++ has 3 different numeric literals: binary, decimal and hexadecimal. Binary and hexadecimal literals are specified
with the following prefixes:

| Literal Type | Prefix | Example  |
|--------------|--------|----------|
| Binary       | `0b`   | `0b1010` |
| Decimal      | `N/A`  | `123`    |
| Octal        | `0o`   | `0o12`   |
| Hexadecimal  | `0x`   | `0x2A`   |

All of these literals support:

- Sign prefix: either `+` or `-`.
- Type postfix: see the section on [numeric type postfixes](../type-system/(Non)-Primitive-Types.md)

Any of the numeric types, as well as the big number types, can be called as regular object initializers, and will
default to `0`.

## Boolean Literal

There are two keywords for boolean literals in S++: `true` and `false`. These are the only two boolean literals in S++,
and are used to represent the `std::boolean::Bool` type. The `std::boolean::Bool` initializer can be called, and will
default the value to `False`.

## Array Literal

The array literal is split into two forms: a non-empty array literal and an empty array literal. The non-empty array
literal has its elements provided within the `[]` tokens, and the element type and number of elements is inferred. Empty
arrays are initialized on definition but none of the elements are set, so the type and size must be explicitly provided
within the `[]` tokens.

| Array variation | Example                              | Type Inference                                 |
|-----------------|--------------------------------------|------------------------------------------------|
| Non-empty       | `let x = [1, 2, 3]`                  | `std::array::Arr[std::bignum::BigNum, 3_uz]`   |
| Empty           | `let x = [std::bignum::BigInt, 100]` | `std::array::Arr[std::bignum::BigInt, 100_uz]` |

For more details see the section on [array types](../type-system/Arrays-Tuples.md).

## Tuple Literal

The tuple literal is a list of different-type items inside the `()` tokens. The type of the tuple is inferred from the
items. For example, `let x = (1, "Hello", 3.14)` infers a
`std::tuple::Tup[std::bignum::bigint::BigInt, std::string::Str, std::bignum::bigdec::BigDec]` type. There is slightly
different syntax
for 1-tuples, to differentiate them from regular parenthesized expressions.

| Tuple Length | Syntax   |
|--------------|----------|
| 0            | `()`     |
| 1            | `(x,)`   |
| 2            | `(x, y)` |
