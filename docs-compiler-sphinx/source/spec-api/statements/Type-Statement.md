# Type Statement

The `type` statement is used to alias types, allowing for more readable code and easier type management. It has full
generic support, and can be used in module, superimposition, of function scopes. The syntax is as follows:

```S++
type TypeName = Type
```

Where `TypeName` is the name of the type alias, and `Type` is the type being aliased. More complex generic types can
also be aliased, such as:

```S++
type MyType[T] = Arr[T, 10] or Map[Str, T]
```

Common uses of the `type` statement are seen in defining the `Opt[T]` and `Res[T, E]` types in the standard library:

```S++
type Opt[T] = Some[T] or None
type Res[T, E] = Pass[T] or Fail[E]
```

## Type System Integration

The types created in `type` statements are **not** new types, but aliases to existing types. This means that they can be
used in place as if they were the original type. For example, if `MyType[T]` is defined as `Arr[T, 10_uz]`, then it can
be used in place of `Arr[T, 10_uz]` in any context where an array of size 10 is expected.

All behaviour on the original type are available on the aliased type. This includes methods, type statements, and
constants. For example, if `MyType[T]` is defined as `Arr[T, 10_uz]`, then it can be used with the `iter_ref` method,
and `::Element` type will be accessible, referring to the element type of the array.
