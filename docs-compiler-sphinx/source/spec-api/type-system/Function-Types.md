# Function Types

## Overview

S++ has three first-class function types. All functions, lambdas and methods are one of these three types. The three
types are:

- `std::function::FunMov[In, Ret]`
- `std::function::FunMut[In, Ret]`
- `std::function::FunRef[In, Ret]`

## Methods

Each type represents the environment capture that takes place. Environment capture doesn't just refer to the `self` of a
method, but also to values used in closures. The type of the function refers to the actual function itself rather than
the parameter types and arguments it receives.

For methods:

| Method                                         | Function Type                     |
|------------------------------------------------|-----------------------------------|
| `fun function(self, a: Str, b: Bool) -> Void`  | `FunMov[(Str, Bool), Void]`       |
| `fun function(&mut self, a: BigInt) -> Void`   | `FunMut[(BigInt,), Void]`         |
| `fun function(&self, a: [BigDec, 10]) -> Void` | `FunRef[(Arr[BigDec, 10]), Void]` |

Static methods are always the `FunRef` type.

## Closures

With closures, the function type depends on the _captures_. This most restrictive convention is used to determine the
function type.

An example closure that has captures:

```S++
let a = 123
let b = 456
let x = |x: BigInt caps a, &b| -> Void { ... }
```

| Most constrictive capture         | Function Type          |
|-----------------------------------|------------------------|
| `\|a: Str, caps x\| -> Void`      | `FunMov[(Str,), Void]` |
| `\|a: Str, caps &mut x\| -> Void` | `FunMut[(Str,), Void]` |
| `\|a: Str, caps &x\| -> Void`     | `FunRef[(Str,), Void]` |

If a closure has a move-based convention, then the closure will be a `FunMov` type. This means that the symbol it is
attached to will be consumed when the function is called. For example, for `let c1 = |caps a| -> Void { ... }`, then
calling `c1()` twice will result in the first call consuming `a`, and the second call will fail with a memory
uninitialized error.

If a closure's most constrictive capture is a mutable borrow, then the closure will be a `FunMut` type. This means that
the symbol it is attached to will be borrowed mutably when the function is called. For example, for
`let c2 = |&mut a| -> Void { ... }`, then `c2` cannot be called, as it is not defined as mutable. The definition
` let mut c2 = ...` is required.
