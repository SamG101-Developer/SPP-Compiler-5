# Ideas

## Lexer
- Support multiline comments (1-char lookahead for `#`, `\n` injection)

## Coroutine Update
- Allow early `ret` inside a coroutine (cannot have an expression).
- Introduce the `GenOnce` type -> acts as `Gen` but with an auto call to `resume()`
- The `GenOnce::resume` must be a consuming method.

## Arrays Update
### Indexing
- Introduce the `[n]` postfix index operator.
- Switch the `.index` operator to tuples only.
- Switch binary folding to tuples only.
- Create `IndexMov`, `IndexMut`, `IndexRef` types.

```S++
cls IndexMut[T] { }
sup [T] IndexMut[T] {
    fun index_mut(&mut self, index: USize) -> GenOnce[&mut T] { }
}

cls IndexRef[T]
sup [T] IndexRef[T] {
    fun index_ref(&self, index: USize) -> GenOnce[&T] { }
}

sup [T] Vec[T] ext IterMut[T] {
    fun index_mut(&mut self, index: USize) -> GenOnce[&mut T] {
        ret self.data.index_mut(index)
    }
}

sup [T] Vec[T] ext IterRef[T] {
    fun index_ref(&self, index: USize) -> GenOnce[&T] {
        ret self.data.index_ref(index)
    }
}
```

## Return Type Overloading
- For the function call, optionally send in a left-hand side target type.
- This is either the type of the assignment target variable, or the optional explicit type of the `let`.
- If a `return_type=` kwarg is provided, match it against the return type.
- No `return_type=` can create ambiguity errors with overloads.
- Remove the return type check from the overload conflict checker.
