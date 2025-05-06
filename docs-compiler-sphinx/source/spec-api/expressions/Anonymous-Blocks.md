# Anonymous Blocks

Anonymous blocks of code are inner scopes that act as expressions. For example, the following code block is an anonymous
block:

```S++
let x = {
    let y = 5
    y + 5
}
```

As blocks defined scopes, symbols defined within the block cannot be accessed from outside the scope. This means that
the symbol `y` cannot be accessed from outside the defined block. All the symbols defined inside the block, that are
still in the initialized state at the end of the block, will have their custom destructors run, if defined, as the end
of the block signifies the end of the scope and therefore the end of the lifetime these symbols can be alive for.