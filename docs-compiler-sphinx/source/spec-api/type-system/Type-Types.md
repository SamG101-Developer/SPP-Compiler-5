# Try Types

Try types, also known as residual types, are types that superimpose `std::ops::try::Try`. This type allows for the
postfix `?` operator to be used, and is provided by a fail and pass type. The STL provides `Try` implementation for the
`Opt[T]` and `Res[T, E]` types:

```S++
sup [T] Opt[T] ext std::ops::try::Try[T, None] {
    fun op_is_output(&self) -> Bool {
        ret *self is Some[T](..)
    }
}


sup [T, E] Res[T, E] ext std::ops::try::Try[T, Fail[E]] {
    fun op_is_output(&self) -> Bool {
        ret *self is Pass[T](..)
    }
}
```

Note the unwrapped "pass" type, but the wrapped "fail" type. This is because the `Try` type needs to compare the wrapped
fail type with the function's return type (check for a match), but if the `?` operator unwraps, then the unwrapped pass
type is needed (for type inference).