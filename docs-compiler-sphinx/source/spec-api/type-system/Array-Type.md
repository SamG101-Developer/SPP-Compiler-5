# Array Type

## Overview

The low level array type in S++ is the `std::array::Arr[T, n]` type. It represents `n` contiguous `size(T)` elements in
memory. It is a first-class type, with safe accessor methods, and is treated in the same way as any other type. The
safety of this type is ensured by using bounds checking and `std::option::Opt[T]` return types.

Arrays should be used when a known-length collection is required, even if the elements aren't all ready at the time the
array is created. For collections with dynamic sizing, see the [vector]() type.

## Syntax

To declare an array, the `[]` tokens must be used, with comma-separated elements inside. Each element is an expression,
and each expression's inferred type must match the first expression's inferred type. The following example creates the
variable `x`, with the type `std::array::Arr[std::string::Str, 3]`.

```S++
let x = ["hello", func(), variable]
```

Sometimes arrays need to be created in an "empty" state, and then have elements filled in. Because type annotations
cannot be given with values, the empty array needs to include the type information itself:

```S++
let x = [std::string::Str, 3]
```

Incidentally, this matches the type exactly: `[std::string::Str, 3]` is the shorthand type for
`std::array::Arr[std::string::Str, 3]`. It should be noted that whilst this creates an empty array, the actual array
object itself is initialized. This is different to:

```S++
let x: [std::string::Str, 3]
```

as in this case, the actual variable is uninitialized, and needs a value set to it before usage.

## Type Rules

As the [memory](../memory/Memory-Model.md) section describes, borrows are second class, and cannot be applied to
attributes of a class. The same goes for arrays: they cannot store (and therefore potentially extend the lifetime of),
borrowed values.

Therefore, whilst creating the type `std::array::Arr[&std::string::Str]` is syntactically valid, it can never actually
be created with values in; the empty-array literal's generic argument is barred from containing a borrow convention.

## Indexing

As with tuples, indexing is done with the `.0` operator, where the index can be any number between 0 and the length of
the array. This is compile-time enforced, to prevent any runtime bounds errors for element access. Because elements
aren't guaranteed to exist in the array, the indexing return type is `std::option::Opt[T]`.

Typically, the `.get` method is used, as runtime values can be passed into the method.
