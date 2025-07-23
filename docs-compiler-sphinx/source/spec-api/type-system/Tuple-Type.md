# Tuple Type

## Overview

The low level tuple type in S++ is the `std::tuple::Tup[..Ts]` type. It represents a collection of variable type
elements, in the same way a class contains attributes. Instead of named access, tuple elements are access by index. This
means that the standard memory rules apply, and `let x = tuple.0` marks `tuple` as partially moved.

The tuple type is readonly, and cannot have elements set into it, only from initialization with the tuple literal.

## Syntax

To declare a tuple, the `()` tokens must be used, with comma-separated elements inside. Each element is an expression,
and each expression can have a different inferred type. A 1-tuple type must have a trailing comma, to differentiate it
from a standard parenthesized expression.

```S++
let tuple1 = ([1, 2],)
let tuple2 = (0, "hello", false)
```

This creates tuples with the types:

- `std::tuple::Tup[std::array::Arr[std::bignum::bigint::BigInt, 2]]`
- `std::tuple::Tup[std::bignum::bigint::BigInt, std::string::Str, std::boolean::Bool]`

Tuples are always declared with values inside them, unlike arrays, which can be created with empty slots.

## Type Rules

As the [memory](../memory/Memory-Model.md) section describes, borrows are second class, and cannot be applied to
attributes of a class. The same goes for tuples: they cannot store (and therefore potentially extend the lifetime of),
borrowed values.

Therefore, whilst creating the type `std::array::Tup[&std::string::Str, &std::boolean::Bool]` is syntactically valid, it
can never actually be created with values in; the tuple literal checks for borrow elements, and there is no "setter" for
elements into a tuple.

## Indexing

As with tuples, indexing is done with the `.0` operator, where the index can be any number between 0 and the length of
the array. This is compile-time enforced, to prevent any runtime bounds errors for element access. Because standard
memory rules are enforced to tuples as with normal classes, indexing always returns a non-wrapped type of the element;
the borrow checker will know if an element has been removed, an error will be thrown if a moved element is moved again.
