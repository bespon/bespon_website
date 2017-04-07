# BespON Specification

This is an overview of the BespON specification.  A more formal,
more detailed specification will follow as soon as the Python implementation
is refined further.  More details are available in the Python implementation,
particularly in `grammar.py` and `re_patterns.py`.


## File format

The default encoding for BespON files is UTF-8.  The default extension
is `.bespon`.

As a text-based format, BespON is specified at the level of Unicode code
points.  Some code points are always invalid as literals within BespON data,
and may only be transmitted in backslash-escaped form within strings.

  * All code points with Unicode `General_Category` Cc (control characters)
    are prohibited as literals, with the exception of the horizontal tab
    U+0009 (`\t`) and line feed U+000A (`\n`).  The carriage return
    U+000D (`\r`) is also allowed as a literal if followed immediately by a
    line feed, in which case the `\r\n` sequence is normalized to `\n`.
    Otherwise, literal `\r` is prohibited.
  * The line separator and paragraph separator U+2028 and U+2029 are
    prohibited as literals.
  * All code points with Unicode property `Bidi_Control` are prohibited as
    literals.  Since these code points can easily cause the appearance of
    text to differ from the actual order in which code points are entered in
    a file, they are not appropriate in a text-based data format meant for
    human editing.
  * The use of a BOM (U+FEFF) is discouraged, since the default encoding
    is UTF-8.  A single BOM at the start of a file or stream is allowed,
    and discarded.  A BOM at any other location is prohibited.
  * All code points with Unicode property `Noncharacter_Code_Point` are
    prohibited as literals.
  * All Unicode surrogate code points (U+D800 – U+DFFFF) are prohibited as
    literals, except when properly paired in an implementation in a language
    whose string representation requires them (UTF-16, UCS-2, etc.).



## None type

None/null/undefined is represented as `none`.  All other capitalizations of
`none` are invalid and must produce errors.  Unlike YAML, uppercase and
titlecase variants of reserved words are NOT equivalent to their lowercase
versions, and other capitalization variants are NOT valid unquoted strings.
The literal string "none", in any capitalization, can only be represented by
using a quoted string.



## Bool

Boolean values are represented as `true` and `false`.  As with `none`, all
other capitalizations are invalid and must produce errors.  The only way
to obtain the literal strings "true" and "false", in any capitalization, is
to use quoted strings.  Unlike TOML, the meanings of `true` and `false` are
NOT context-dependent; they are not strings when used as dict keys, but booleans
when used as dict values.




## Numbers

### Integers

Decimal, hexadecimal, octal, and binary integers are supported.  Base
prefixes for non-decimal numbers are `0x`, `0o`, and `0b`; other
capitalizations are prohibited.  A single underscore is allowed after a
base prefix before the first digit, and single underscores are allowed
between digits (for example, `0x_12_34`).  Hexadecimal values may use either
uppercase `A-F` or lowercase `a-f`, but mixing cases is prohibited.

Signs `+` and `-` may be separated from the first digit character by spaces
or tabs, but this is discouraged.  Breaking a line between a sign and the
number to which it belongs is prohibited.

Implementations in languages that lack an integer type must interpret
integers as floats.

Implementations are expected to use 32-bit unsigned integers at minimum.
Any integer value that cannot fit in an implementation's integer type must
result in an error, rather than an integer overflow or undefined behavior.

### Floats

Decimal and hexadecimal floats are supported.  Decimal floats use `e` or `E`
for the exponent, while `p` or `P` are used for hex.  Single underscores
are allowed after the base prefix, between digits, and before exponents
(for example, `0x_12_34_p5_6`).

Signs `+` and `-` may be separated from the first digit character by spaces
or tabs, but this is discouraged.  Breaking a line between a sign and the
number to which it belongs is prohibited.

Implementations are expected to use float types compatible with IEEE 754
binary64.

Infinity is represented as `inf`, and not a number as `nan`.  All other
capitalizations are invalid, and the literal strings "inf" and "nan" require
quoted strings.



## Unicode strings

Unicode normalization is not performed on the Unicode string type, to avoid
potential information loss issues.  Unicode normalization before saving data
in BespON format, or after loading data, is encouraged as appropriate.

### Unquoted strings

Unquoted strings that fit the pattern for an ASCII identifier and are not
a variant of `none`/`true`/`false`/`inf`/`nan` may be used anywhere,
including as dict keys.  These must match the regular expression
`_*[A-Za-z][0-9A-Z_a-z]*`.

Implementations should provide an option to enable unquoted strings based on
Unicode identifiers, using Unicode properties `XID_Start` and `XID_Continue`
with the omission of the Hangul filler code points U+115F, U+1160, U+3164,
and U+FFA0 (which typically are rendered as whitespace).  This is not the
default because of the confusability and security implications of using
unquoted non-ASCII code points.

Implementations should also provide an option to disable unquoted strings.
This can be useful when it is desirable to avoid any potential for ambiguity.

### Quoted inline strings

Quoted inline strings are delimited with one or more single quotation marks
`'`, double quotation marks `"`, or backticks `` ` ``.

Backslash escapes are enabled within strings delimited by single and double
quotation marks.  Escapes of the forms `\xHH`, `\uHHHH`, `\U00HHHHHH`, and
`\u{H...H}` are all allowed, with the restriction that all non-numeric hex
characters must have the same case (uppercase or lowercase) within a given
escape.

Strings delimited by single and double quotation marks follow the same rules.
A string that starts with one quotation mark `'` or `"` ends at the next
identical quotation mark that is not backslash-escaped.  The sequences `''`
and `""` represent the empty string.  Longer delimiter sequences such as
`'''` and `"""` may be used to include any unescaped delimiter sequence that
is shorter or longer than the delimiters.  Such delimiter sequences must be
multiples of 3 characters in length and no longer than 90 characters.

Strings delimited by backticks begin with a delimiter sequence of length
1, 2, 3, or a multiple of 3 no longer than 90 characters, and end when the
same delimiter sequence is next encountered.  This is similar to Markdown.
These are literal strings; there are no backslash escapes.  If the first
non-space character at the beginning or end of a literal string is a
backtick, then one space at that end of the string is stripped.  This allows,
for example, the sequence ``` `` ` `` ``` to represent the single
backtick `` ` ``.

Inline quoted strings may be wrapped over multiple lines.  When this is done,
the indentation of the first continuation line must be equal to or greater
than that of the line on which the string begins, and any subsequent
continuation lines must have that same indentation.  Wrapped quoted strings
are unwrapped by replacing each line break with a space if the last character
before the break does not have the Unicode property `White_Space`, and simply
stripping breaks otherwise.

### Quoted block strings

Quoted block strings preserve literal line breaks and indentation relative to
the closing delimiter.  They start with a pipe `|` followed by a sequence of
single or double quotation marks or backticks.  The rest of the line after
this opening sequence must contain nothing but whitespace (space, tab, line
feed).  The sequence must be a multiple of 3 characters in length and no
longer than 90 characters.  The string ends when the same sequence of
quotation marks/backticks is found between a pipe `|` and a slash `/`.  The
sequence must not appear unescaped anywhere else within the string.  Shorter
or longer sequences of quotation marks/backticks are allowed unescaped.

For example,
``````text
|```
First line
    second line
|```/
``````
would be equivalent to `"First line\n    second line\n"`.  Note that literal
line breaks and indentation relative to the closing delimiter are preserved.
When a block string starts at the beginning of a line, the opening and
closing delimiters must have the same indentation.  Otherwise, the closing
delimiter must have indentation greater than or equal to that of the line
on which the block string begins.

The choice of `'` and `"` versus `` ` `` in the delimiters determines whether
backslash escapes are enabled.  When they are, a backslash followed
immediately by zero or more spaces and a literal newline becomes the empty
string.  Thus,
``````text
|"""
First line\
Second line
|"""/
``````
would be equivalent to `"First lineSecond line"`.



## Lists

Lists are ordered collections of objects.  Objects are not all required to be
of the same type.

By default, an implementation must raise an error if the total nesting depth
of all collection objects (lists and dicts) exceeds 100.

There are two list syntaxes.  In indentation-based syntax, list elements are
denoted with asterisks `*`.  For example,
```text
* 'First element'
* 'Second element'
```
Indentation between the asterisk and the beginning of the following object
is strongly encouraged, but not required.  Indentation may be spaces or tabs.
If the indentation character immediately before and after the `*` is a tab,
then the `*` is ignored in calculating the total indentation; otherwise it
is treated as equivalent to a space.  In indentation-based syntax, all `*`
in a list must have the same indentation, and all objects that follow them
must also have the same indentation.

When a list is within a list, each successive asterisk must be on a new line.
Thus,
```text
*
  * text
```
is equivalent to
```text
[[text]]
```

An asterisk cannot be used alone without a following object to represent the
empty list.  The empty list must always be represented explicitly as `[]`.

There is also a more compact, inline syntax for lists, in which the list is
delimited by square brackets `[...]` and individual list elements are
separated by commas.  For example,
```text
['First element', 'Second element']
```
Everything within an inline list must have indentation greater than or equal
to that of the line on which the list started.  While logical and consistent
indentation beyond this is encouraged, it is not enforced in any way.



## Dicts

Dicts are mappings of keys to values.

By default, an implementation must raise an error if the total nesting depth
of all collection objects (lists and dicts) exceeds 100.

Only `none`, `true`, `false`, integers, strings, byte strings, and derived
types are allowed as keys.  Floating point numbers and collection types are
specifically excluded.  Floating point numbers are problematic as keys due to
rounding, and because `nan` is not equal to itself.  Collection types can be
problematic as keys depending on how mutability is handled, and are not
supported as keys in some programming languages.

Duplicate keys are strictly prohibited.

As with lists, there are two syntaxes for dicts.  In indentation-based syntax,
all keys must have the same indentation, and values must have indentation
consistent with their keys.  Keys and values are separated by equals signs
`=`.  For example,
```text
key = value
another_key = 'another value that
    continues'
yet_another_key =
    sub_dict_key = sub_dict_value
```
Quoted values that start immediately after their keys (on the same line) may
have the same indentation as their keys, following the rules for continuation
lines for quoted strings.  This is convenient when it is desirable to avoid
indentation.  However, indenting values is encouraged.

There is also a more compact, inline syntax for dicts that parallels that for
inline lists.  A dict is delimited by curly braces `{...}` and individual
key-value pairs are separated by commas.  For example,
```text
{key = value, another_key = another_value}
```
As with inline lists, everything within an inline dict must have indentation
greater than or equal to that of the line on which the dict started.  While
logical and consistent indentation beyond this is encouraged, it is not
enforced in any way.



## Key paths

Key paths provide a compact syntax for expressing nested dicts (and to a
lesser extent lists).  A key path is a sequence of period-separated,
unquoted strings that are suitable as dict keys.  For example,
```text
key.subkey.subsubkey = 123
```
would be equivalent to
```text
key = {subkey = {subsubkey = 123}}
```

A key path can only pass through dict nodes that do not yet exist, or that
do exist but have only ever been visited previously as part of a key path.
The final element of a key path must not have been defined previously,
because that would violate the prohibition on duplicate keys.  Thus,
```text
key.subkey.subsubkey = 123
key.subkey.another_subsubkey = 456
```
would be valid and equivalent to
```text
key = {subkey = {subsubkey = 123, another_subsubkey = 456}}
```
However,
```text
key.subkey = {}
key.subkey.another_subsubkey = 456
```
would be invalid, because it is attempting to define `key.subkey` both as
an empty dict and also as a dict `{another_subsubkey = 456}`.

The final element of a key path may alternatively be an asterisk `*`, in
which case it adds a list element.  Thus,
```text
key.subkey.* = 123
key.subkey.* = 456
```
would be equivalent to
```text
key = {subkey = [123, 456]}
```

Key paths are scoped.  All key path nodes created from within a given dict
are accessible from within that dict.  However, all of those nodes become
inaccessible once the dict is closed.  Thus, in
```text
key =
    subkey.subsubkey = 123
```
it would be possible to add `subkey.another_subsubkey` at the `subkey` level,
because key paths based on `subkey` are still within scope.  However, it
would not be possible to use `key.subkey.another_subkey` at the `key` level,
since that is outside the scope.



## Sections

Sections provide a way to use indentation-based syntax without using
deep indentation.  A section is started by a pipe `|` followed by a sequence
of equals signs `=` whose length is a multiple of 3 and is no longer than 90
characters.  This is followed by a key path or a key, which must terminate
on the line where the key path begins (line breaks are not permitted).
Everything after the section start is included under the specified key path
or key.  For example,
```text
|=== section.subsection
key = value
another_key = another_value
```
would be equivalent to
```text
section = {subsection = {key = value, another_key = another_value}}
```

Sections may also use the asterisk `*` as a key, to assemble a list while
avoiding the associated indentation in normal syntax.  For example,
```text
|=== *
key = value

|=== *
another_key = another_value
```
is equivalent to
```text
[{key = value}, {another_key = another_value}]
```

A section ends at the next section.  Alternatively, it is possible to return
to the top (root) level of the data structure by using the section closing
element, which has the form `|===/`.  This parallels the delimiters for block
strings.  However, when this is used to close a section, the number of equals
signs `=` in the closing element must match the number used to open the
section.  Furthermore, if the closing element is ever used, then ALL sections
must be closed explicitly.



## Tags

BespON provides for explicitly typed objects, with the tagging syntax
`(tag)>`.  Support for tags will be added to the Python implementation soon.
By default, tags will only be used to support binary types and perhaps a few
other types beyond those already discussed.

Tag syntax makes possible byte strings.
```text
(bytes)> 'Some text'
```
It also makes possible arbitrary binary data.
```text
* (base16)> '536F6D652074657874'
* (base64)> 'U29tZSB0ZXh0'
```

Tag syntax will eventually provide an optional extension mechanism for
user-defined types.



## Right-to-left code points

BespON is intended for human editing.  This can be difficult with
code points from right-to-left languages (code points with Unicode
`Bidi_Class` R or AL), because it is possible for a key and a value to be
reversed in visual representation due to the bidirectional text rendering
algorithms.  For example, suppose we have the data
```text
א =
  1
ב =
  2
```
In this form, the meaning is clear, as a mapping of Hebrew letters to
integers.  However, put these values on a single line, and the order of keys
and values is lost at the visual level (though still retained in terms of
logical code point ordering).
```text
{א = 1, ב = 2}
```
This is the same as
```text
{\u05D0 = 1, \u05D1 = 2}
```

Under ideal circumstances, a rendering engine would identify that this is a
data as opposed to text context, and provide a useful rendering.  Given that
this will rarely be possible, the next best thing would be to require that
right-to-left code points only appear in contexts in which this sort of
key-value reversal in visual rendering is not possible.

By default, whenever a string contains code points with Unicode `Bidi_Class` R
or AL on its last line, no string, number, or comment is allowed to follow it
on that line.  Any following object must be on a subsequent line, to avoid the
potential of confusion due to bidirectional rendering.  Such a string may
still be followed by a comma `,`, bracket `]`, brace `}`, equals sign `=`, or
other non-string, non-digit element, since this will not introduce the
possibility of ambiguous rendering.



## Comments

Comments come in two forms.

Line comments start with a single number sign `#` that is not followed
immediately by another `#`, and go to the end of the line.  Line comments may
optionally be preserved in round tripping that only modifies data, as opposed
to adding or deleting values.  However, line comments cannot in general
survive round tripping, because they may appear anywhere, with any
indentation, in any quantity.  So far as syntax is concerned, they are not
uniquely associated with any particular data element.

Doc comments are uniquely associated with individual data objects.  Each data
object may have at most one doc comment.  The doc comment must come before
the object, and may only be separated from it by a tag (doc comments come
before tags).  Doc comments come in two forms.  Inline doc comments start
with three number signs `###`, or a sequence that has a length that is a
multiple of 3 and is no longer than 90.  They follow the same rules as inline
quoted strings, with two additional restriction in indentation-based
syntax:

  * A doc comment must have the same indentation as its object.
  * If a doc comment starts at the beginning of a line, it cannot be followed
    on its last line by anything (other than a line comment).

Doc comments also come in a block form, that follows the same rules as block
strings:
```text
|###
Block doc comments.

These can contain empty lines.
|###/
```
The rules about indentation-based syntax apply to these as well.

Because doc comments are uniquely associated with individual data objects,
they may survive round tripping even when data is added or removed.



## Roadmap

Some possible features are still under consideration, and may be added either
as required features or as optional extensions.

  * Support for labeling values in dicts or elements in lists, and then
    referring to them elsewhere by label to create aliases or copies.
  * Support for a dict to inherit initial values or default fallback values
    from another dict.  Support for dict merging.
