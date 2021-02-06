# BespON Specification

This is an overview of the BespON specification.  A more formal,
more detailed specification will follow as soon as the Python implementation
is refined further.  Additional details are available in the
[Python implementation](https://github.com/gpoore/bespon_py),
particularly in `grammar.py` and `re_patterns.py`.


## File format

The default encoding for BespON files is UTF-8.  The default extension
is `.bespon`.

As a text-based format, BespON is specified at the level of Unicode code
points.  Some code points are always invalid as literals within encoded BespON
data, and may only be transmitted in backslash-escaped form within strings.

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

None/null/nil is represented as `none`.  All other capitalizations of
`none` are invalid and must produce errors.  Unlike YAML, uppercase and
titlecase variants of keywords words are NOT equivalent to their lowercase
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

Infinity is represented as `inf`, and not-a-number as `nan`.  All other
capitalizations are invalid, and the literal strings "inf" and "nan" require
quoted strings.

Implementations are expected to use float types compatible with IEEE 754
binary64.  Any non-`inf` float value that cannot fit in an implementation's
float type must result in an error by default, rather than overflowing to
`inf`.



## Unicode strings

Unicode normalization is not performed on the Unicode string type, to avoid
potential information loss issues.  Unicode normalization before saving data
in BespON format, or after loading data, is encouraged as appropriate.

### Unquoted strings

Unquoted strings that fit the pattern for an ASCII identifier and are not a
variant of `none`/`true`/`false`/`inf`/`nan` or a reserved word based on `inf`
or `nan` may be used anywhere, including as dict keys.  These must match the
regular expression `_*[A-Za-z][0-9A-Z_a-z]*`.

Implementations should provide an option to enable unquoted strings based on
Unicode identifiers, using Unicode properties `XID_Start` and `XID_Continue`
with the omission of the Hangul filler code points U+115F, U+1160, U+3164,
and U+FFA0 (which typically are rendered as whitespace).  This is not the
default because of the confusability and security implications of using
unquoted non-ASCII code points.

Implementations should also provide an option to disable unquoted strings.
This can be useful when it is desirable to avoid absolutely any potential for
ambiguity.

### Quoted inline strings

Quoted inline strings are delimited with one or more single quotation marks
`'`, double quotation marks `"`, or backticks `` ` ``.

Backslash escapes are enabled within strings delimited by single and double
quotation marks.  Escapes of the forms `\xHH`, `\uHHHH`, `\U00HHHHHH`, and
`\u{H...H}` are all allowed, with the restriction that all non-numeric hex
characters must have the same case (uppercase or lowercase) within a given
escape.

Strings delimited by single and double quotation marks follow the same rules.
A string delimited by only one quotation mark `'` or `"` begins immediately
after the opening quotation mark and ends immediately before the next
identical quotation mark that is not backslash-escaped.  The sequences `''`
and `""` represent the empty string.  Longer delimiter sequences such as `'''`
and `"""` can be used to minimize the need for backslash escapes.  Such
delimiter sequences must be multiples of 3 characters in length and no longer
than 90 characters.  The string begins immediately after the opening delimiter
sequence and ends immediately before the next occurrence of the sequence that
is not backslash-escaped and is not part of a longer sequence of the delimiter
character.  A string using these longer delimiters can include any unescaped
sequence of the delimiter character that is shorter or longer than the
delimiter sequence, with one exception.  The first and last characters in a
string must be backslash-escaped if they are the delimiter character.  This
prevents any ambiguity about the beginning and end of the string.

Strings delimited by backticks begin with a delimiter sequence of length
1, 2, 3, or a multiple of 3 no longer than 90 characters, and end when the
same delimiter sequence is next encountered.  This is similar to Markdown.
These are literal strings; there are no backslash escapes.  If the first
non-space character at the beginning or end of a literal string is a
backtick, then one space at that end of the string is stripped.  This allows,
for example, the sequence `` ` ``` ` `` to represent the triple
backticks ` ``` `.

Inline quoted strings may be wrapped over multiple lines.  When this is done,
the indentation of the first continuation line must be equal to or greater
than that of the line on which the string begins, and any subsequent
continuation lines must have that same indentation.  Wrapped quoted strings
are unwrapped by replacing each line break with a space if the last character
before the break does not have the Unicode property `White_Space`, and simply
stripping breaks otherwise.

### Quoted multiline strings

Quoted multiline strings preserve literal line breaks and indentation relative
to the closing delimiter.  They start with a pipe `|` followed by a sequence
of single or double quotation marks or backticks.  The rest of the line after
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
When a multiline string starts at the beginning of a line or is only preceded
by whitespace, the opening and closing delimiters must have the same
indentation.  Otherwise, the closing delimiter must have indentation greater
than or equal to that of the line on which the multiline string begins.

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



## Indentation

Collection types (lists and dicts) may be represented with an
indentation-based syntax.  Both spaces and tabs are allowed as indentation,
although use of spaces is strongly encouraged.

If spaces and tabs are mixed in indentation, total indentation level is
determined by the exact, literal sequence of spaces and tabs, *never* by
converting tabs into some equivalent number of spaces.



## Lists

Lists are ordered collections of objects.  Objects are not all required to be
of the same type.

By default, an implementation must raise an error if the total nesting depth
of all collection objects (lists and dicts) exceeds 100.

There are two list syntaxes.  In indentation-based syntax, list elements are
denoted with asterisks `*`.  An asterisk must not be preceded on its line by
anything except for indentation.  For example,
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
Asterisks in sub-lists must be indented relative to those in higher-level
lists.  Thus,
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
to that of the line on which the list starts.  The only exception is if an
inline list occurs within an inline collection type, in which case it inherits
the indentation level of the parent collection, and everything within it must
have indentation greater than or equal to that indentation level.  While
logical and consistent indentation beyond this is encouraged, it is not
enforced in any way.



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
all keys must have the same indentation.  A key must not be preceded on its
line by anything except for indentation (and an asterisk `*` if in a list, or
a tag if explicitly typed).  Values must have indentation consistent with
their keys.  Values that do not follow their keys on the same line must be
indented relative to their keys.  Keys and values are separated by equals
signs `=`.  For example,
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
greater than or equal to that of the line on which the dict started.  The only
exception is if an inline dict occurs within an inline collection type, in
which case it inherits the indentation level of the parent collection, and
everything within it must have indentation greater than or equal to that
indentation level.  While logical and consistent indentation beyond this is
encouraged, it is not enforced in any way.

In an indentation-style dict, an equals sign `=` must be on the same line as
the end of its key.  In an inline-style dict, an equals sign is permitted to
be the first thing on the line immediately following the end of its key to
provide resiliance against poor line breaking, but purposely doing this is
strongly discouraged.



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
since that is outside the scope.  Scoping ensures that all data for a given
dict is somewhat localized.



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
element, which has the form `|===/`.  This parallels the delimiters for
multiline strings.  However, when this is used to close a section, the number
of equals signs `=` in the closing element must match the number used to open
the section.  Furthermore, if the closing element is ever used, then *all*
sections must be closed explicitly.



## Aliases

Aliases are used to reference objects that have previously been
[labeled](spec_overview.md#labels).  Aliases consist of a dollar sign `$`
followed immediately by a label, which is an unquoted string.

When an alias refers to a dict, then key path-style `$alias.key.subkey`
notation is supported to refer to objects inside the dict.  This avoids having
to label each dict value explicitly.

There are also two special aliases that always exist.  `$~` refers to the
top level of the data structure.  Since `~` is not a valid unquoted string,
this alias can never be overwritten by the user.  Similarly, `$_` is an
alias to the current collection.  This can be useful in a list to insert
a reference to itself (`$_`) or in a dict to reuse the value of an
earlier key (`$_.earlier_key`).

Implementations must provide an option to disable aliases, since they add some
additional complexity and indirection, and it may be desirable to avoid using
them under some circumstances.  (The complexity involved is not as great
as might be imagined, though.  In the Python implementation, resolving aliases
only takes around 140 lines of code more than the non-alias case.)

Aliases are not permitted as dict keys.  This would make it significantly
harder for a user to determine whether duplicate keys exist.  It would
also make `$alias.key.subkey` syntax ambiguous.  (Is it a single key
located at `$alias.key.subkey`, or a key path consisting of `$alias` followed
by `key.subkey`?)

By default, implementations must check for circular references and raise an
error when they are detected.  Implementations should provide optional support
for circular references.



## Tags

BespON provides for explicitly typed objects, with the tagging syntax
`(tag)>`.  By default, tags will only be used to support binary types and
perhaps a few other types beyond those already discussed.  Tag syntax will
eventually provide an optional extension mechanism for user-defined types.

Tags also allow data to be labeled for later referencing via aliases,
allow the indentation and newlines in a string to be specified in
a shorthand form, and permit inheritance for collections.

### Binary types

Tag syntax makes possible byte strings.
```text
(bytes)> 'Some text'
```
It also makes possible arbitrary binary data.
```text
* (base16)> '536F6D652074657874'
* (base64)> 'U29tZSB0ZXh0'
```

When a binary type is applied to a string delimited by double or single
quotation marks, only `\xHH` escapes are permitted.

The `bytes` type can only be applied to strings containing literal code points
in the ASCII range (before any backslash-escaping is applied).

The exact requirements for `base16` and `base64` typed strings may still be
refined in the future.  Using a string containing backslash-escapes for
`base16` or `base64` is currently permitted but discouraged.  The current
string requirements for both types are relatively strict.  It is possible
that this may be relaxed somewhat.

The `base16` type must only be applied to strings in which all non-numeric hex
characters have the same case (uppercase or lowercase).  Multiline strings and
inline strings wrapped over multiple lines are permitted (all trailing spaces
and line feeds on each line are stripped before processing), but leading
whitespace on a line and trailing empty lines at the end of a string are
prohibited.  Each two-character sequence (representing a byte) may be
separated from the next two-character sequence with a single space, but only
if this is done throughout the entire string; otherwise, internal whitespace
is prohibited.

The `base64` type follows similar rules to `base16`.  Multiline strings are
permitted (all trailing spaces and line feeds on each line are stripped before
processing), but leading whitespace on a line and trailing empty lines at the
end of a string are prohibited.  Internal whitespace within a line is
prohibited, and as a result, using `base64` with wrapped inline strings is not
possible.  Inline strings that are not wrapped, with no leading or trailing
whitespace, are permitted.

### Labels

Tags allow data objects to be labeled, for later referencing via aliases.
For example,
```text
(bytes, label=bin_data)> 'Some text'
```
A label must always be an unquoted string.  Allowing arbitrary code points in
labels would have confusability implications.

Labels are currently not allowed for dict keys.

When a label and a type occur in a tag, the type must always be first.  The
type may be omitted when the default type for the following object is desired
and the default type may be inferred.  In practice, this means that for
standard, non-binary types, the type may always be omitted except in the case
of dicts in indentation-style syntax.  In those cases, the type is currently
required.  This restriction may be removed once label and alias rules are
further refined.  (Dict keys are not currently allowed to be labeled, to
parallel the fact that aliases currently are not allowed as keys.  However,
if dict keys were allowed to be labeled, then that could make a label at the
beginning of an indentation-style dict ambiguous.  Does it apply to the dict
or to the first key?)

### Strings

The tag keywords `indent` and `newline` may be applied to strings to customize
indentation and newline sequences.  These are only allowed for multiline
strings.

`indent` specifies a sequences of spaces and tabs that is added to the
beginning of each line that follows a literal (not escaped) line break (as
well as the first line).

`newline` specifies a sequence of code points that is used to replace all
literal line feeds (`\n`).  Only the empty string and code point sequences
considered a newline in the Unicode standard
([chapter 5.8, "Newline Guidelines"](http://www.unicode.org/versions/Unicode9.0.0/ch05.pdf))
are permitted:
```text
['', '\r\n', '\n', '\v', '\f', '\r', '\x85', '\u2028', '\u2029']
```
There is the further restriction that only newline sequences in the ASCII
range are permitted for strings that are explicitly typed with a binary
type (for example, `bytes`).


### Inheritance

Dicts support two tag keywords for inheritance.  `init` specifies an alias
or inline list of aliases to dicts that are used for initialization.  All
the keys supplied by these dicts must not duplicate each other or duplicate
the keys directly entered in a dict using `init`.  The prohibition on
duplicate keys still holds.  `default` specifies an alias or inline list
of aliases to dicts that are used to supply defaults.  Because these are
default, fallback values, duplicate keys are allowed, and do not overwrite
existing keys.  For example,
```pycon
>>> bespon.loads("""
initial =
    (dict, label=init)>
    first = a
default =
    (dict, label=def)>
    last = z
    k = default_v
settings =
    (dict, init=$init, default=$def)>
    k = v
""")
{'initial': {'first': 'a'},
 'default': {'last': 'z', 'k': 'default_v'},
 'settings': {'first': 'a', 'k': 'v', 'last': 'z'}}
```

Lists also support two tag keywords for inheritance.  `init` specifies an
alias or inline list of aliases to lists whose elements are inserted at the
beginning of a list using `init`.  `extend` specifies an alias or inline list
of aliases to lists whose elements are appended at the end of a list using
`extend`, after all explicit elements have been inserted.  For example,
```pycon
>>> bespon.loads("""
initial_1 = (label=init1)> [1, 2]
initial_2 = (label=init2)> [3, 4]
extend = (label=ex)> [7]
settings = (init=[$init1, $init2], extend=$ex)> [5, 6]
""")
{'initial_1': [1, 2],
 'initial_2': [3, 4],
 'extend': [7],
 'settings': [1, 2, 3, 4, 5, 6, 7]}
```

Additional inheritance-related features, including a recursive merge for
dicts, are under consideration.



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
optionally be preserved in round-tripping that only modifies data, as opposed
to adding or deleting values.  However, line comments cannot in general
survive round-tripping, because they may appear anywhere, with any
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

  * A doc comment must have the same indentation as its object, unless the
    object is tagged, in which case the doc comment must have the same
    indentation as the tag.
  * If a doc comment starts at the beginning of a line, it cannot be followed
    on its last line by anything other than a line comment.

Doc comments also come in a multiline form, that follows the same rules as
multiline strings:
```text
|###
Multiline doc comments.

These can contain empty lines.
|###/
```
The rules about indentation-based syntax apply to these as well.

Because doc comments are uniquely associated with individual data objects,
they may survive round-tripping even when data is added or removed.



## Extended types

An implementation may provide optional, non-default support for additional
types.  The exact set of recommended optional types, and their precise
definition, may be revised in the future; this is not guaranteed to be stable.
Even once the set of recommended optional types stabilizes, implementations
may support additional, optional, language-specific data types that are in
common use; for example, the Python implementation provides optional support
for tuples.

### Numbers

* **Rational number literals** use the form `1/2`, where the numerator and
  denominator must both be decimal integers, and any sign must come before the
  fraction (with optional, discouraged whitespace after the sign and on both
  sides of the slash).
* **Complex number literals** use the general form `1.0+2.0i`, where the real
  part is optional, the imaginary unit is represented with `i`, and numbers
  must be floats (either both in decimal or both in hex form, unless one
  is `inf` or `nan`).

To allow for the possibility of complex number literals, and provide the
widest possible scope for their definition, three letters are currently
reserved as number literal units: `i`, `j`, and `k`.  This means that `infi`,
`infj`, `infk`, `nani`, `nanj`, `nank`, and all capitalization variants are
reserved words.  This technically would allow for quaternion literals,
although that is not currently planned.

### Collections

* `set`:  Applied to a list to return an unordered collection in which all
  objects are unique.
* `odict`:  Ordered dict, in which key order is preserved.



## Roadmap

Some possible features are still under consideration, and may be added either
as required features or as optional extensions.

  * `copy` and `deepcopy` types based on aliases.
  * Support for recursive dict merging.
