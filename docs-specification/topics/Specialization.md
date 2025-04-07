# Specialization

```
cls SomeType[T] {
    using type = T
}

sup SomeType[Str] {
    using type = Vec[Str]
}

sup SomeType[T] where [T: Copy] {
    using type = Set[T]
}
```