# Hello World

<primary-label ref="header-label"/>

<secondary-label ref="doc-complete"/>

## Project Setup

Create a folder called `HelloWorld`, and inside the folder, run the following command to create a new S++ project.

```bash
spp init
```

## Writing the Code

This will create the project structure, and import standard library. Open the `main.spp` file, and write the following
code:

```
fun main() -> Void {
    std::print("Hello, World!");
}
```

## Running the Code

To run the code, use the following command:

```bash
spp run --release
```

This will compile the code, and run the binary.
