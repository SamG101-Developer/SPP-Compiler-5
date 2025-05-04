# Ideas

## Lexer

- Support multiline comments (1-char lookahead for `#`, `\n` injection)

## Looping

- Analyse the body of a loop block twice for memory safety.

## Slicing

- Slicing can be done with `let slice = vector.iter_mut().slice(5, 10) => Gen[&mut BigInt]`.
- Setting a new value into a slice is more difficult.
- Setting an array index doesn't work with index syntax: `vector[0] = 5`.
    - Typechecks `&mut BigInt <-> BigInt => FAIL`
    - Would need to use a `.set` or `.place` method.
        - `vector.set(0, 5)` or `vector.place(0, 5)`.
    - For slicing:
        - `vector.set_slice(5, 10, other.iter_mov())`

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
