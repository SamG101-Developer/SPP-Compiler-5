# Variant Type

## Overview

In S++, variant types are runtime-tagged types with no syntactic wrapping. They are represented by the
`std::variant::Var[..Ts]` type, where each generic argument in the variadic generic parameter `Ts` represent one of the
composite types.

## Syntax

To declare a variant type, the `or` keyword is used between the composite types:

```S++
use VarType = Str or BigInt or Bool
```

## Type Rules

The type equality method will match a value that is any one of the composite types to the variant type, but not vice
versa as it isn't a guaranteed match. For example, `fun func(a: VarType) -> Void` can be called as `func("hello")` as
`std::string::Str` is a composite type of `VarType`. However, a `std::string::Str` parameter cannot accept a `VarType`
argument, because the argument could contain a `BigInt` or `Bool` value.

There is no way to construct a variant type from the type-name, because the composite type isn't stored inside the
variant type, but is stored _as_ the variant type. For example, the type `VarNumType = U8 or U64` is represented as a
64-bit space in memory, but will only have 8-bits taken up when a `U8` object is being stored. Because the value isn't
an attribute, the object-initialization can't accept a value.

This is remedied by provided both a type hint and a value to a `let` statement:

```S++
let x: VarNumType = 123_u8
```

The following steps are applied for explicit variant types:
1. The `let` statement is defined with a variant "explicit type", and a value.
2. The value's type is inferred: the "inferred type".
3. The explicit type is type checked against the inferred type.
4. Type checking matches a composite type inside a variant type.
5. The "explicit type" is assigned to the symbol.

## Assignment

The assignment is the same as the `let` statement:

```S++
let mut x: VarNumType = 123_u8
x = 456_u64
```

## Pattern Matching

See the section on [flow typing]() for more detail.
