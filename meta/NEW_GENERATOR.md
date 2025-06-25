# Next Generation Coroutines & Generators

Coroutines are a first class system in S++. They are the entire backbone of the language's concurrency model. Iterations
exclusively relies on coroutines, that yield into a generator type. The generator type is a first class type, and allows
for iteration over a sequence of values, or even errors.

## Generators

A coroutine is defined with the `cor` keyword, rather than the standard `fun` for subroutines. The return type must
extend the `Gen` type. There are 3 different generator types known to the compiler:

- `Gen[Yield, Send=Void]`
- `GenOpt[Yield, Send=Void]`
- `GenRes[Yield, Err, Send=Void]`

The standard generator type can only yield values that match the `Yield` type. This is used for iteration, and indexing
what doesn't have bounds checking. It is safe to assume that every `.res()` call to the generator will yield a value of
type `Yield`, until the generator is exhausted.

The `GenOpt` type is used for optional generators. It can yield values of type `Yield`, or it can yield a "no-value",
interpreted as the `Void` type. Yielding `Opt[&T]` is impossible, because `Some[T]` contains a `val: &T`, which violates
second class borrow rules. Therefore, the optionality of yielded values must be tied into the generator itself, with the
receiver part of the protocol handling the destructure.

Similarly, the `GenRes` type is used for fallible generators. It can yield values of type `Yield`, or it can yield an
error of `Err` type. The `Err` type must be specified in the generator type. Again, the coroutine receiver part of the
protocol handles the destructure of the result.

## Yielding Values

Depending on the type of generator, values can be yielded in different ways. The `gen` keyword is used with an
expression, to yield a value of type `Yield`. This is the standard way to yield a value from a coroutine.

```S++
cor f() -> Gen[BigInt] {
    gen 1  # Yield a value of 1
    gen 2  # Yield a value of 2
}
```

To yield optionally, the `gen` keyword can be used without an expression. This will yield a "no-value". Note that the
`Yield` type cannot be `Void`, so there is never a conflict between yielding a value and yielding a "no-value". This
optional yielding is seen a lot in getting en element from a container for example.

```S++
cor f() -> GenOpt[BigInt] {
    gen 1  # Yield a value of 1
    gen    # Yield a no-value (equivalent to yielding Void)
    gen 2  # Yield a value of 2
}
```

To yield a result, the `gen` keyword can be used with an expression that matches the `Yield` type, or an error that
matches the `Err` type. This is used for fallible generators, where the result can be either a value or an error.

```S++
cor f() -> GenRes[BigInt, CustomError] {
    gen 1              # Yield a value of 1
    gen CustomError()  # Yield an error of type CustomError
    gen 2              # Yield a value of 2
}
```

### Sending Values In

The `gen` keyword is not a statement, but an expression. This means that it can be used for assignment, like
`let x = gen 1`. Thi is how values are received inside the coroutine.

## Handling Yielded Values

To handle yielded values from a generator, the `.res()` postfix operator is used. This operator advances the generator
forward, and receives a `Generated` type (or `GeneratedOpt` or `GeneratedRes` for optional and fallible generators).
These types have their own destructure block, similar to the `case-of` block, but called `iter`.

This block allows the different states of the generator to be handled. The `iter` block can handle: a value being
yielded; a "no-value" being yielded; an error being yielded; an exhausted generator:

```S++
cor f() -> GenRes[BigInt, CustomError] {
    gen 1              # Yield a value of 1
    gen CustomError()  # Yield an error of type CustomError
    gen 2              # Yield a value of 2
    ret                # Mark the generator as exhausted
}

fun main() -> Void {
    let generator = f()  # Get the generator from the coroutine
    iter generator.res() of
        val {
            std::io::print("Value yielded: ", val)  # "val" is of type BigInt
        }
        !error e {
            std::io::print("Error occurred: ", e)   # "e" is of type CustomError
        }
        !! {
            std::io::print("Generator exhausted")
        }
}
```

And for optional generators:

```S++
cor f() -> GenOpt[BigInt] {
    gen 1  # Yield a value of 1
    gen    # Yield a no-value (equivalent to yielding Void)
    gen 2  # Yield a value of 2
    ret    # Mark the generator as exhausted
}

fun main() -> Void {
    let generator = f()  # Get the generator from the coroutine
    iter generator.res() of
        val {
            std::io::print("Value yielded: ", val)  # "val" is of type BigInt
        }
        _ {
            std::io::print("No value yielded")
        }
        !! {
            std::io::print("Generator exhausted")
        }
}
```

It should be notes that not every branch is required; there might only be a branch for if a value is present, like when
getting an element from an array:

```S++
fun main() -> Void {
    let vector = Vec::from([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    let iterator = vector.iter_ref()  # Get an iterator over the vector
    let elem1 = iterator.res()

    iter elem1 of
        val {
            std::io::print("Value yielded: ", val)  # "val" is of type &BigInt
        }
    }
}
```

The generic argument `once` is used to auto unwrap the yielded value, so that it can be used directly without needing
the `iter` block. This is useful for simple cases like indexing a vector.

```S++
fun main() -> Void {
    let vector = Vec::from([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    let element = vector.index_ref(0)  # element is of type &BigInt, no unwrapping needed
}
```

The reason this cannot be used for iterating, is there needs to be a way to know that the generator is exhausted. This
is hwy the `loop ... in ...` syntax is used, as behind the scenes, it applies the block of the `loop` expression every
time value is yielded, but stops adds an `exit` statement for when the generator has exhausted. The transformation looks
like:

```S++
loop element in vector.iter_ref() {
    std::io::print("Value yielded: ", element)
}
```

```S++
let __iterator = vector.iter_ref() 
loop true {
    iter __iterator.res() {
        val {
            std::io::print("Value yielded: ", val)
        }
        !! {
            exit  # Exit the loop when the generator is exhausted
        }
    }
}
```

This closely resembles how Rust would iterate a generator, but instead of hooking into the type system, which second
class borrows can't combine with, there is an exclusive control flow that allows for coroutines.