# Smart Pointers

<primary-label ref="header-label"/>

<secondary-label ref="doc-wip"/>

## Smart Pointers

S++ doesn't use raw pointers in code anywhere. However, there must be a way to store information on the heap, especially
for hierarchical casting. There are a few different smart pointers that allow for the use of the heap:

- `Single[T]`: A simple heap-allocated pointer. This is the most basic smart pointer, and analogous to C++'s
  `std::unique_ptr<T>` or Rust's `Box<T>` type. This is used for single ownership.
- `Shared[T]`: A reference-counted pointer. This is used for shared ownership, and is analogous to C++'s
  `std::shared_ptr<T>` type. It maintains counters for the number of strong and weak references to the data. Like Rust's
  `Rc<T>` type, the internal data is immutable, to follow the strict memory safety rules of S++.
- `Shadow[T]`: A weak reference to a reference-counted pointer. This is used to break cycles in reference-counted
  pointers, and is analogous to C++'s `std::weak_ptr<T>` and Rust's `Weak<T>` type.
- `Thared[T]`: A thread-safe reference-counted pointer. This is used for shared ownership across threads, and is
  analogous to C++'s `std::shared_ptr<T>` type with an `std::atomic<int>` counter, and Rust's `Arc<T>` type.

### `Single[T]`

The `Single[T]` type is similar to Rust's `Box[T]` and C++'s `std::unique_ptr<T>`. It is used for single ownership of
heap-allocated data. The `Single[T]` type is a smart pointer that owns the data it points to, and will deallocate the
data when it goes out of scope. There are cast function overloads for the `Single[T]` type, because the value it points
to in memory may have additional information for the subtype.

```
let x = Single(data=5)
```

Member access into a `Single[T]` is identical to accessing members of the `T` type; there is no need to dereference the
pointer. Whilst `data=` is required to set the value, `.data` is not accessible nor does it exist at all; it just
provides a uniform way to set the initial value.

### `Shared[T]`

The `Shared[T]` type is similar to Rust's `Rc<T>` and C++'s `std::shared_ptr<T>`. It is used for shared ownership of
heap-allocated data. It maintains two counters: a strong reference count, and a weak reference count. The strong
reference count is incremented when the `Shared[T]` type is cloned, and decremented when it is dropped. The weak
reference count is incremented when a `Shadow[T]` type is created from the `Shared[T]` type, and decremented when the
`Shadow[T]` value gets dropped.

```
let x = Shared(data=5)
```

Member access into a `Shared[T]` is also identical to accessing members of the `T` type - there is no need to
dereference the pointer. The counters are available to access (privately), and are merged with the members of the `T`
type.

Like Rust's `Rc<T>` type, the internal data is immutable, to follow the strict memory safety rules of S++. This means
that for mutation to take place, one of the slot types must be used. For example:

```
let x = Shared::new(data=RefSlot::new(5))
let b = x.borrow_mut()
let c = x.borrow_mut()  # Error (already mutably borrowed)
```

```
let x = Shared::new(data=RefCellSlot::new(5))
{
  let b = x.borrow_mut()
}
let c = x.borrow_mut()  # No error
```

```
let x = Shared::new(data=MutexSlot::new(5))
let b = x.borrow_mut()
```

### `Shadow[T]`

The `Shadow[T]` type is similar to Rust's `Weak<T>` and C++'s `std::weak_ptr<T>`. It is used to break cycles in
reference-counted pointers. The `Shadow[T]` type is created from a `Shared[T]` type, and will increment the weak
reference count of the `Shared[T]` type. The `Shadow[T]` type can be upgraded to a `Shared[T]` type, which will
increment the strong reference count of the `Shared[T]` type.

```
let x = Shared(data=5)
let y = x.shadow()
```

Member access into a `Shadow[T]`, like for `Shared[T]`, is identical to accessing members of the `T` type - there is no
need to dereference the pointer.

### `Thared[T]`

The `Thared[T]` type (**Th**read-safe Sh**ared**) is similar to Rust's `Arc<T>` and C++'s `std::shared_ptr<T>` type with
an `std::atomic<int>` counter. It is used for shared ownership of heap-allocated data across threads. The `Thared[T]`
type maintains the same two counters as `Shared[T]`, but with `Atomic[U32]` types.
