# Pinning

Pinning is an important concept in S++, and it is done automatically by the compiler. Pinning forces a symbol to not
move in memory, until all pins for that symbol are released. A symbol with more than 0 "pins" is sai d to be "pinned".
A "pin" can be any other symbol (see examples).

## Usages

### Coroutine Calling

When a coroutine is called, and there is a borrow convention parameter, the argument being borrowed (if symbolic) is
pinned. This is typically the case for function calls, as whilst borrowing a temporary like `&1` is possible, it is
rare.

```S++
cor g(a: &BigInt) -> Gen[Yield=Str] {
    gen "a" * a
}

fun f() -> Void {
    let a = 1
    let generator = g(&a)
}
```

In this example, the symbol `a` is pinned when the coroutine `g` is called. This means that the symbol `a` cannot be
moved in memory until the coroutine `g` is finished executing. This is important because if the coroutine `g` were to
yield, the symbol `a` were to be moved in memory, and then the coroutine `g` were to be resumed, the symbol `a` would be
non-initialized in memory, yet there would still be a usable borrow to it from inside the coroutine `g`.

Therefore, `a` is pinned until the generator goes out of scope (guaranteed to have finished executing). Note that
because `a` is pinned as an argument, the entire generator must be pinned as-well. Therefore, not only is `a` pinned,
but so is `generator`. The reason behind is that the generator _contains_ the borrow- it cannot be returned, as this
would potentially extend the lifetime of the borrow beyond the associated owned object's lifetime.

This means that `generator` can not be returned. It can however be yielded out of a coroutine, as this guarantees that
control is returned to the caller, forcing the owned object to outlive its borrow.

### Async functions

As asynchronous functions operate as coroutines, the same rules apply:

```S++
fun g(a: &BigInt) -> Str {
    ret "a" * a
}

fun f() -> Void {
    let a = 1
    let future = async g(&a)
}
```

Again, both `a` and `future` are pinned, for the same reasons as the coroutine pinning logic above.

### Lambda functions

The final use of pinning objects is when capturing borrows into lambda functions. This is because again, borrows cannot
outlive their owned objects:

```S++
fun f() -> Void {
    let a = 1
    let lambda = |caps &a| "a" * a
}
```

In this example, the symbols `a` and `lambda` are pinned.
