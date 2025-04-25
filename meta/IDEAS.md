# Ideas

## Lexer

- Support multiline comments (1-char lookahead for `#`, `\n` injection)

## Coroutine Update

- Allow early `ret` inside a coroutine (cannot have an expression).
- Introduce the `GenOnce` type -> acts as `Gen` but with an auto call to `resume()`
- The `GenOnce::resume` must be a consuming method?
- Need a `res/step/next` keyword for generators.
    - This will allow the actual `Yield` type to be returned.
    - The borrow system is capable of invalidating borrows so this is fine.
- Add a special rule in the function resolution that maps the keyword to `.resume()`
- Can add a lhs type-analysis check to ensure `Gen` is superimposed.

## Arrays Update

## Return Type Overloading

- For the function call, optionally send in a left-hand side target type.
- This is either the type of the assignment target variable, or the optional explicit type of the `let`.
- If a `return_type=` kwarg is provided, match it against the return type.
- No `return_type=` can create ambiguity errors with overloads.
- Remove the return type check from the overload conflict checker.

## Generic Inference

- Upgrade to infer from variant parts as-well
- For example, `case x is std::option::Some(val)` should infer `T` from `x`, and not require
  `std::option::Some[std::string::Str]` as it currently does.

## Lambdas / Closures

- Need to decide on a syntax => probably mirror function syntax closely.
- Syntax needs to now look cludgy when used as a function argument.
- Potentially no need to support generic lambdas.
- For example, `(a: BigInt) -> Void { ... }` looks alright, but as an argument:
  - Like: `f((a: BigInt) -> Void { ... }, other_args)` the double `((` looks cludgy.
- Alternatives:
  - `|a: BigInt| { ... }`
  - `|&x, &mut y, a: BigInt, b: Bool| -> Void { ... }`
  - Need a way to mark coroutines. Maybe `cor | ... | -> Void { }`
- In argument:
  - `f(|a: BigInt| { ... }, other_args)`
- Allow function types to _defer_ to more constricting, ie allow a `FunMut` for a `FunMov` parameter.