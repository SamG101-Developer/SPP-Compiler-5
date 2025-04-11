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

With closures, the function type depends on the _captures_. This section is under development because closures aren't
implemented yet, but the general gist is that a closure type matches the most-constrictive capture:

```S++
let a = 123
let b = 456
let x = fun (x: BigInt) with (a, &b) -> Void { ... }
```

This creates a `FunMov` type, because it can only be called once; once the captured value is consumed once, the closure
cannot be called again.
