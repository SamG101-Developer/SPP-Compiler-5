# Anonymous Blocks

Anonymous blocks of code are inner scopes that act as expressions. For example, the following code block is an anonymous
block:

```S++
let x = {
    let y = 5
    y + 5
}
```

After the block, as there is no symbol leakage, `y` is not accessible. Anonymous blocks can be used to create temporary
variables that are only accessible within the block. They can also be used to group statements together, or to create
temporary scopes for variables.
