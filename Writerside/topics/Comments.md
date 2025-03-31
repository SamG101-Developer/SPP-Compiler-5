# Comments

<primary-label ref="header-label"/>

<secondary-label ref="doc-complete"/>

## Comment Types

S++ supports 3 major types of comments: single-line comments, multi-line comments, and inline comments. Borrowed from
Python, the `#` comment is used for single-line comments. Multi-line comments are wrapped in `##` characters, and can
span multiple lines. Inline comments are syntactically identical to multi-line comments, just on a single line.

## Single-line Comments

<secondary-label ref="doc-complete"/>

<secondary-label ref="feature-impl"/>

Single-line comments are denoted with a single `#` character, followed by any character, terminating with a newline.
They can be on their own line, or at the end of a line of code. Any Unicode character can be used in a single-line
comment:

```
# This is a single-line comment
let x = 5  # This is also a single-line comment
```

## Multi-line Comments

<secondary-label ref="doc-complete"/>

<secondary-label ref="feature-impl"/>

Multi-line comments are denoted by `##` characters at the start and end of the comment. They wor the same as Python's
`"""` comments, or C++'s `/* */` comments. They can span multiple lines, and any Unicode character can be used in a
multi-line comment:

```
##
This is a multi-line comment
This can span multiple lines
##
```

## Inline Comments

<secondary-label ref="doc-complete"/>

<secondary-label ref="feature-impl"/>

Inline comments are syntactically identical to multi-line comments, but are placed within a line of code:

```
func(param1: ## important ## : std::Str) -> std::Void { }
```
