# Anonymous Blocks

<primary-label ref="header-label"/>

<secondary-label ref="doc-complete"/>

Anonymous blocks of code are inner scopes that act as expressions. For example, the following code block is an anonymous
block:

```
let x = {
    let y = 5;
    y + 5
};
```

After the block, as there is no symbol leakage, `y` is not accessible. Anonymous blocks can be used to create temporary
variables that are only accessible within the block. They can also be used to group statements together, or to create
temporary scopes for variables.

## Scoping lifetimes

Inner scopes can be used to activate the destructors of variables. Some of these have specific usages such as the
`RefSlot` type:

```
let x = Shared::new(RefSlot::new(5))
let a = x.borrow_mut()
let b = x.borrow_mut()  # Error (already mutably borrowed)
```

```
let x = Shared::new(RefSlot::new(5))
{
    let a = x.borrow_mut()
    # BorrowMut[T] destructor runs, reducing the borrow count
}
let b = x.borrow_mut()  # No error, as the lifetime of `a` has ended
```
