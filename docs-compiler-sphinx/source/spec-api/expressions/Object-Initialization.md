# Object Initialization

All non-variant types in s++ can be initialized using the **uniform object initialization** (UOI) syntax. This syntax is
used
to create instances of types, and provides a single, simple way to create objects of any type.

UOI is the only way to initialize a type in S++, and follows simple rules:

- An argument can be given per attribute, with the attribute name as the key.
- If the argument name matches the attribute name, the attribute name can be omitted (shorthand).
- Any attribute can be omitted, and will be defaulted (see below).

## Example:

```S++
cls MyType {
    x: U64
    y: Str
}

fun f() -> Void {
    let my_obj1 = MyType(x=1_u64, y="hello")
    let my_obj2 = MyType(x=2_u64)
    let my_obj3 = MyType()
}
```

## Defaulting missing attributes

Every type has a default value: for numbers, it is 0, for string it is the empty string etc. For all non-compiler known
types, it calls the object initializer for that type, recursively doing the same for all attributes, until compiler
known types are reached.

Given the following classes:

```S++
cls MyType {
    x: U64
    y: Str
}

cls MyOtherType {
    a: MyType
    b: U64
}

cls MyThirdType {
    c: MyOtherType
}
```

The object initialization for `MyThirdType` will, fully expanded, look like this:

```S++
let my_obj = MyThirdType(c=MyOtherType(a=MyType(x=0_u64, y=""), b=0_u64))
```

Class attributes can be given customized default values, which bypasses the typical "reduce until compiler known types"
method. The following example shows how to do this:

```S++
cls MyType {
    x: U64 = 1_u64
    y: Str = "hello"
}
```

This changes the full expansion from above, for `MyThirdType`, to:

```S++
let my_obj = MyThirdType(c=MyOtherType(a=MyType(x=1_u64, y="hello"), b=0_u64))
```

Note that the default value isn't any expression, but a [constant expression](../statements/Cmp-Statement.md#constant).
This means that the default value must be a literal, or an object initialization that only contains literals or other
object initializations. This is to ensure that the default value is always the same, and doesn't change at runtime.

### Default from another object

There is an additional, special way to "fill in" missing attributes from another object of the same type. This is done
by using the `..` operator. The syntax looks like this:

```S++
let my_obj = MyType(x=1_u64, y="hello", ..other_obj)
```

As `other_obj` is fully initialized, the `..` operator will move or copy all attributes from `other_obj` that are not
present in the initializer. This is useful for creating objects that are similar to another object, but with some
attributes changed. The `..` operator can only be used with objects of the same type, and will not work with objects of
different types, even if they have the same attributes, enforcing the robust type system of S++.
