# BespON:  Bespoken Object Notation


BespON is a configuration language with several unique features.

  * **Multi-paradigm** – Do you like JSON's braces, brackets, and quotation
    marks?  Would you rather leave out some quotation marks and use
    significant indentation instead of braces and brackets?  Do you prefer
    INI-style sections, with no braces or brackets *and* no indentation?
    BespON supports all three styles.

  * **Extensible** – Support for several standard data types is built in,
    and other types may be supported soon using tag syntax.

  * **Round-trip enabled** – Many config languages lack parsers that can
    round-trip data.  Loading, modifying, and then saving can change data
    ordering, resulting in unnecessarily complicated diffs.  Even when a
    round-trip parser exists, comments may be lost or associated with the
    wrong data objects.  BespON is designed with round-tripping in mind,
    including doc comments that are uniquely associated with individual data
    objects and thus can be preserved through arbitrary data manipulation.

Take a look:

```text
# Line comments are allowed!  They can be round-tripped as long as data
# elements are only modified, not added or removed.

### This is a doc comment.  It can always be round-tripped.###
# Only one doc comment is allowed per object; another couldn't be here.

"quoted key with \x5C escapes" = 'quoted value with \u{5C} escapes'

`literal key without \ escapes` = ``literal value without `\` escapes``

# ASCII identifier-style strings are allowed unquoted.  Keys cannot contain
# spaces; values can contain single spaces and must be on one line.
# Unquoted Unicode identifiers can optionally be enabled.
unquoted_key = unquoted value

inline_dict = {key1 = value1, key2 = value2,}  # Trailing commas are fine.

inline_list_of_ints = [1, 0x12, 0o755, 0b1010]  # Hex, octal, and binary!

list_of_floats =
  * 1.2e3
  * -inf  # Full IEEE 754 compatibility.  Infinity and NaN are not excluded.
  * 0x4.3p2  # Hex floats, to avoid rounding issues.

wrapped_string = """string containing no whitespace lines in which line breaks
    are replaced with spaces, and "quotes" are possible by via delimiters"""

multiline_literal_string = |```
        A literal string in which linebreaks are kept (as '\n')
        and leading indentation (relative to delimiters) is preserved,
        with special delimiters always on lines by themselves.
    |```/

multiline_escaped_string = |"""
    The same idea as the literal string, but with backslash-escapes.
    |"""/

key1.key2 = true  # Key path style; same as "key1 = {key2 = true}"

|=== section.subsection  # Same as "section = {subsection = {key = value}}"
key = value
|===/  # Back to root level.  Can be omitted if sections never return to root.
```



## Why?

[![XKCD Standards](https://imgs.xkcd.com/comics/standards.png)](https://xkcd.com/927/)

Now the requisite XKCD reference is out of the way, why BespON?

  * **Comments**.  And doc comments that are uniquely associated with
    individual data objects, and thus may always be round-tripped correctly.
  * **Trailing commas**.
  * **Unquoted strings**.  But only identifier-style strings or unambiguous
    number-unit style strings (like `12pt`), and never broken across a line.
  * **Multiline strings** with indentation preserved *relative to delimiters*.
    Multiline strings with obvious leading/trailing whitespace, since it's
    inside delimiters.
  * **Integers**.  And integers with various bases (decimal, hex, octal,
    binary).
  * **Full IEEE 754 floating point support** (with infinity and NaN),
    including hex floats for cases when rounding errors aren't acceptable.
  * **Immutable data object model**.  Duplicate keys are invalid and must
    result in an error.
  * **A small list of special characters**.  Every ASCII punctuation character
    does NOT have its own, special meaning.  No constant wondering about what
    is allowed unquoted, and if it will appear as itself or something else.
  * **Sections and key paths** for conveniently representing nested data
    structures, without ending up with bracket soup or half a page width of
    indentation.
  * **"Acceptable" performance** even when completely implemented in an
    interpreted language.



## Getting started

A [Python implementation](https://github.com/gpoore/bespon_py) is available
now.  It supports loading and saving data.  Round trip support for modifying
data is almost complete and is coming very soon.

There is also a
[language-agnostic test suite](https://github.com/bespon/bespon_tests),
which the Python implementation passes.



## Stability

All current features are expected to be stable.  The objective is a final
version 1.0 of the Python implementation by the end of summer 2017.



## Specification

A [brief overview](spec_overview.md) is currently available.  More
technical details are in the Python implementation, particularly in
`grammar.py` and `re_patterns.py`.  A more formal, more detailed
specification will follow as soon as the Python implementation is refined
further.
