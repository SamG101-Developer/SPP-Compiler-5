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
### Indexing
- Introduce the `[n]` postfix index operator syntax.
- The `[n]` syntax will map to either `get_ref` or `get_mut`
- The `[mut n]` syntax will map to `get_mut`

## Return Type Overloading
- For the function call, optionally send in a left-hand side target type.
- This is either the type of the assignment target variable, or the optional explicit type of the `let`.
- If a `return_type=` kwarg is provided, match it against the return type.
- No `return_type=` can create ambiguity errors with overloads.
- Remove the return type check from the overload conflict checker.
