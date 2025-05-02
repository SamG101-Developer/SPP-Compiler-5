# Ideas

## Lexer

- Support multiline comments (1-char lookahead for `#`, `\n` injection)

## Looping

- Analyse the body of a loop block twice for memory safety.
- Check the iterator convention from the iterable.
  - `loop x in vector.iter_mut()` => `Gen[&mut T]` => `&mut T` is the type of `x`.

## Slicing

- Slicing can be done with `let slice = vector.iter_mut().slice(5, 10) => Gen[&mut BigInt]`.
- Setting a new value into a slice is more difficult.
- Setting an array index doesn't work with index syntax: `vector[0] = 5`.
    - Typechecks `&mut BigInt <-> BigInt => FAIL`
    - Would need to use a `.set` or `.place` method.
        - `vector.set(0, 5)` or `vector.place(0, 5)`.
    - For slicing:
        - `vector.set_slice(5, 10, other.iter_mov())`

## Coroutine Update

- Introduce the `GenOnce` type -> acts as `Gen` but with an auto call to `.res()`
- The `GenOnce::resume` must be a consuming method?

## Return Type Overloading

- For the function call, optionally send in a left-hand side target type.
- This is either the type of the assignment target variable, or the optional explicit type of the `let`.
- If a `return_type=` kwarg is provided, match it against the return type.
- No `return_type=` can create ambiguity errors with overloads.
- Remove the return type check from the overload conflict checker.

## Generic Inference

- Upgrade to infer from variant parts as-well
- For example, `case x is std::option::Some(val)` should infer `T` from `x`, and not require
  `std::option::Some[std::string::Str](val)` as it currently does.

## MAJOR ISSUE

- If a pinned value is returned with no intermediate symbol storage.


## Deferred Generic Inference (NOT CONFIRMED AS A FEATURE)
- Dont require all generics to be known when a type is created.
- If a generic is needed, it must have been inferred at the point it is needed.
- Allow using a method or attribute being set to infer the generic type.

```
let x = []  # std::vector::Vec[T=?]
x.push(5)   # T=std::number:bigint::BigInt
```
