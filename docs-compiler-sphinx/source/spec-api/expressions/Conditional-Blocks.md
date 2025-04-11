# Conditional Blocks

S++ conditional blocks combine standard if-else statements with pattern-matching. This simplifies the language by
reducing the number of constructs needed to handle conditional logic.

## Basic Branching

The following example shows the most basic version of the `case-else` block. It follows the standard `if-else` syntax of
most programming languages.

```S++
case some_condition {
    std::console::print("hello world")
}
else case some_other_condition_1 {
    std::console::print("hello galaxy")
}
else case some_other_condition_2 {
    std::console::print("hello universe")
}
else {
    std::console::print("hello multiverse")
}
```

## Imitation Ternary

There is no `?:` ternary operator, as the `case` and `else` keywords can be used to achieve the same result. This also
follows the "left-ro-right" reading order of the language.

```S++
let result = case some_condition { "true" } else { "false" }
```

## Partial Fragments (Expressions)

Partial fragments can be used to introduce multiple comparisons or pattern matches against the same value. Each
comparison contains a pattern fragment, which when combined with the partial fragment, creates a full pattern. Fragments
are joined by a comparison operator: `==`, `!=`, `<`, `>`, `<=`, `>=`, or `is`.

This subsection focuses on regular comparison operators, while the `is` operator is discussed in a later section.
Pattern fragments are introduced with the `of` keyword.

```S++
case person of
    == john { "hello john" }
    == jane { "hello jane" }
else { "hello stranger" }
```
```S++
case age of
    <= -1 { "error" }
    == 00 { "newborn" }
    <  18 { "child" }
    <  60 { "adult" }
else { "senior" }
```

Partial expression are expanded into their full form by the compiler: the first `case` expression effectively becomes
`case person.eq(john) { }`. See [binary operator expansion]() for more information on expansion.

## Multiple Pattern Fragments

Multiple pattern fragments can be used on the same branch, separated by a comma. This allows for more complex pattern
matching, and can be used to match multiple values at once.

```S++
case person of
    == john, jane { "hello john or jane" }
    == jack, jill { "hello jack or jill" }
else { "hello stranger" }
```

Multiple pattern fragments per branch can only be used with non-`is` pattern fragments. The reason behind this is
explored in the destructuring sections.

## Destructuring Objects

Destructuring objects in a pattern match is done by using the `is` operator. This follows the standard binary `is`
functionality, where the right-hand-side can be a destructure of any variation.

```S++
case person of
    is Person(name="john", ..) { "hello john" }
    is Person(name="jane", ..) { "hello jane" }
else { "hello stranger" }
```

The `..` token is used to mark missing attributes.

## Destructuring Variant Objects

Because equality checks of variants can match their inner types (if the variant is the let-hand-side), the `is` operator
can be used for destructuring a vairiant object.

```S++
case optional of
    is Some[Str](val) { "some" }
    is None { "none" }
```

> Due to current generic implementations, `Some[Str](val)` must be used instead of `Some(val)`. There is an issue with
> generics inside variant types. This will be fixed in a future release.

## Destructuring Generic Types

There is no keyword-equivalent to C++'s `if constexpr(...)` to check generic types inside a function. As such,
destructuring generic types was introduced to allow for pattern matching on generic types.

```S++
fun func[T](a: T) -> Void {
    case a of
        is Str() { std::console::print("Str") }
        is U32() { std::console::print("U32") }
}
```

## Destructuring Tuples, Arrays

Tuples and arrays can be destructured, because their size is known, and so the number of elements in the pattern match
can be verified. Unless the `..` token is present, as with object identifiers, all elements must be matched. The `..`
token can appear anywhere in the pattern match, but only once per pattern.

```S++
case tuple of
    is (1, ..) { "tuple starts with 1" }
    is (2, ..) { "tuple starts with 2" }
else { "tuple is something else" }
```

```S++
case array of
    is [1, ..] { "array starts with 1" }
    is [2, ..] { "array starts with 2" }
else { "array is something else" }
```

## Destructuring with Bindings

Variables can be bound during a destructure, and used in the branch. This allows for more complex pattern matching, and
can be used to extract values from the object. Destructures that contain bindings are expanded into `let` statements, as
their semantics are almost identical.

Note that for nested bindings, such as `Line(point=Point(a, b), ..)`, the variable `point` does exist, but in a
partially moved state, because `let a = point.a` and `let b = point.b` will have both been executed to get the values
for `a` and `b`.

```S++
case tuple of
    is (a, 1) { "tuple is ($a, 1)" }
    is (b, 2) { "tuple is ($b, 2)" }
else { "tuple is something else" }
```
```S++
case array of
    is [a, 1] { "array is [$a, 1]" }
    is [b, 2] { "array is [$b, 2]" }
else { "array is something else" }
```
```S++
case person of
    is Person(name="john", age, ..) { "hello john, you are ${age}" }
    is Person(name="jane", age, ..) { "hello jane, you are ${age}" }
else { "hello stranger" }
```

Patterns can be nested too, to any depth and with any combination of object/variant/array/tuple destructuring, enabling
highly complex pattern matching.

## Pattern Guards on Destructures

Pattern guards can only be used on destructures, as the `and` would conflict with normal expressions.

```S++
case person of
    is Person(name="john", age, ..) and age < 18 { "hello john, you are a child" }
    is Person(name="john", age, ..) and age < 60 { "hello john, you are an adult" }
    is Person(name="john", age, ..) { "hello john, you are a senior" }
else { "hello stranger" }
```

