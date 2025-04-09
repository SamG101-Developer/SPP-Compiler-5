# Literals

## String Literal

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

S++ has 3 different numeric literals: binary, decimal and hexadecimal. Binary and hexadecimal literals are specified
with the following prefixes:

| Literal Type | Prefix | Example  |
|--------------|--------|----------|
| Binary       | `0b`   | `0b1010` |
| Hexadecimal  | `0x`   | `0x2A`   |
| Decimal      | `N/A`  | `123`    |

All of these literals support:
- Sign prefix: either `+` or `-`.
- Type postfix: see the section on [numeric type postfixes](../type-system/(Non)-Primitive-Types.md)


Any of these types, as well as the big number types, can be called as regular object initializers, and will default to
`0`.

## Boolean Literal

There are two keywords for boolean literals in S++: `true` and `false`. These are the only two boolean literals in S++,
and are used to represent the `std::boolean::Bool` type. The `std::boolean::Bool` initializer can be called, and will
default the value to `False`.

## Array Literal

The array literal is a list of same-type items inside the `[]` tokens. The type of the array, and its size, are inferred
from the items. For example, `let x = [1, 2, 3]` infers a `std::array::Arr[std::number::BigNum, 3]` type. Note that the
size of an array is fixed, so it might be necessary to use the `std::vector::Vec` type if the size is unknown. All
elements must be the same type. For more details see the section on [array types](../type-system/Arrays-Tuples.md).

Empty arrays must be given a type and size, so the literal for empty arrays is `let x = [std::number::BigInt, 100]`.
This tells the compiler to allocate 100 elements of the `BigInt` type, but no value will be set in the slots.

## Tuple Literal

The tuple literal is a list of different-type items inside the `()` tokens. The type of the tuple is inferred from the
items. For example, `let x = (1, "Hello", 3.14)` infers a
`std::tuple::Tup[std::number::BigNum, std::string::Str, std::number::BigDec]` type. There is slightly different syntax
for 1-tuples, to differentiate them from regular parenthesized expressions.

| Tuple Length | Syntax   |
|--------------|----------|
| 0            | `()`     |
| 1            | `(x,)`   |
| 2            | `(x, y)` |
