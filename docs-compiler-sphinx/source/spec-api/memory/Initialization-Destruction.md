# Initialization &amp; Destruction

## Storing on the Stack

### Stack Initialization

Objects are allocated onto the stack when a types object initializer is called. Any number of arguments can be passed,
and any attributes that haven't been given corresponding arguments are "default-constructed". This means that types are
recursively created, down to "primitive" types, which are initialized as so:

| Type                                      | Default Value |
|-------------------------------------------|---------------|
| `std::number::[U/I/F][8/16/32/64/128/256` | `0`           |
| `std::boolean::Bool`                      | `false`       |
| `std::array::Arr[T]`                      | `[]`          |
| `std::string::Str`                        | `""`          |

This creates a simple initialization scheme, where the user can choose to initialize only the attributes they want to.
Default attribute values can be customized by giving attributes on the type a default value. This is done by using the
`=` operator in the attribute declaration.

```
cls Point {
    x: U32 = 10
    y: U32 = 20
    z: U32 = 30
}
```

## Storing on the Heap

### Heap Initialization

Objects can be allocated on the heap, using one of the smart pointer types:

- `std::ptr::single::Single[T]`: Uniquely owned pointer (`std::unique_ptr<T>`, `std::boxed::Box<T>`)
- `std::ptr::shared::Shared[T]`: Reference counted pointer (`std::shared_ptr<T>`, `std::rc::Rc<T>`)
- `std::ptr::shadow::Shadow[T]`: Weak pointer (`std::weak_ptr<T>`, `std::rc::Weak<T>`)
- `std::ptr::thared::Thared[T]`: Thread-safe reference counted pointer (`std::shared_ptr<T>`, `std::sync::Arc<T>`)
