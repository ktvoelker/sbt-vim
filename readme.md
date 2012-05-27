
SBT-Vim Bridge
==============

This is a Vim plugin that allows [sbt](https://github.com/harrah/xsbt/wiki) to
be used from within [Vim](http://www.vim.org/).

Usage:

    :pyfile sbt-vim.py
    :py sbt_compile()

This puts you into Vim's
[quickfix](http://vimdoc.sourceforge.net/htmldoc/quickfix.html) mode, where you
can jump between compilation errors with `:cn` and `:cp`.

The first time you compile, an interactive sbt session will be created in the
background. This can be slow, but subsequent compiles will be faster.

To-Do:

1. A vim script that adds nicer bindings
2. Proper vim plugin packaging
3. Support for `sbt test`

