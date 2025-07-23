# Generator Blocks

As discussed in the [coroutine section](../concurrency-parallelism/Concurrency.md), the yielded value must be inspected
by a special syntactic structure. Second class borrows prevent types like `Opt[&T]` from being yielded, so in this
example, `GenOpt[&T]` is used. This doesn't store the borrow inside a type, but the generator is aare that there may not
be a value associated with the generated value.

The `iter` block is used to inspect the different states of a generated value. A generator type will always yield a
`Generated` type, mirroring the type of generator doing the yielding:

| Generator Type                  | Generated Type             |
|---------------------------------|----------------------------|
| `Gen[Yield, Send=Void]`         | `Generated[Yield]`         |
| `GenOpt[Yield, Send=Void]`      | `GeneratedOpt[Yield]`      |
| `GenRes[Yield, Err, Send=Void]` | `GeneratedRes[Yield, Err]` |

The `GenOnce` assumes type doesn't have a mirroring `Generated` type, as it attempts to inspect a value directly.

## Basic Branching

The structure of an `iter` block resembles a `case-of` block directly, with different branch patterns available, to
inspect different generator states.

There are a total of four different states the at generated values can be in (some states are specific to certain
`GeneratedXXX` types, enforced at compile time):

### Present Value

If a value is present it is destructured by simply providing a variable name. The created variable will have a type that
matches the `Yield` argument exactly, including the potential borrow convention. This is the most common case, and the
syntax is as follows:

```S++
iter generated_value of
    variable { ... }
```

### No Value Present

If an optional generator is used, it may yield a value that indicates that there is no value present. The underscore `_`
token is used to indicate that there is no value present, in the same way it is used to skip a value in standard
destructuring. The syntax for this is as follows:

```S++
iter generated_value of
    _ { ... }
```

### Error Present

If a fallible generator is used, it may yield an error value. The `!` token, followed by a variable to bind the
exception to, is used to indicate that an error is present. The created variable will have a type that matches the `Err`
argument exactly. The syntax for this is as follows:

```S++
iter generated_value of
    !exception { ... }
```

### Exhausted Generator

If a generator has exhausted all values, it can be indicated by using the `!!` token. This indicates that the generator
has no more values to yield; either the end of the coroutine has been reached, or the coroutine has been explicitly
terminated with an early `ret`, possibly conditional. The syntax for this is as follows:

```S++
iter generated_value of
    !! { ... }
```

## Compatibility

### `Gen`

For the standard generator block, the `Generated[Yield]` value can be in two states: either a value is present, or the
generator has exhausted all values. The syntax for this is as follows:

```S++
iter generated_value of
    variable { ... }
    !! { ... }
```

### `GenOpt`

For the optional generator block, the `GeneratedOpt[Yield]` value can be in three states: a value is present, no value
is present, or the generator has exhausted all values. The syntax for this is as follows:

```S++
iter generated_value of
    variable { ... }
    _ { ... }
    !! { ... }
```

### `GenRes`

For the fallible generator block, the `GeneratedRes[Yield, Err]` value can be in three states: a value is present, an
error is present, or the generator has exhausted all values. The syntax for this is as follows:

```S++
iter generated_value of
    variable { ... }
    !exception { ... }
    !! { ... }
```
