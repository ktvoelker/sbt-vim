
SBT-Vim Bridge
==============

This is a Vim plugin that allows [sbt](https://github.com/harrah/xsbt/wiki) to
be used from within [Vim](http://www.vim.org/).

Please [email me](mailto:ktvoelker@gmail.com) if you have questions.

Dependencies
------------

* Vim, compiled with Python support (check with `vim --version | grep +python`)
* SBT on your `$PATH` (check with `which sbt`)

Installation
------------

If you use [Pathogen](https://github.com/tpope/vim-pathogen), just clone this
repository in your `bundles` directory:

    git clone https://ktvoelker@github.com/ktvoelker/sbt-vim.git ~/.vim/bundles/sbt-vim

Otherwise, you will need to copy some files:

    mkdir -p ~/.vim/plugin ~/.vim/python
    git clone https://ktvoelker@github.com/ktvoelker/sbt-vim.git
    cd sbt-vim
    cp plugin/* ~/.vim/plugin/
    cp python/* ~/.vim/python/

Usage
-----

To compile:

    :sbtc

This puts you into Vim's
[quickfix](http://vimdoc.sourceforge.net/htmldoc/quickfix.html) mode, where you
can jump between compilation errors with `:cn` and `:cp`.

The first time you compile, an interactive sbt session will be created in the
background. This can be slow, but subsequent compiles will be faster.

You can also run your tests:

    :sbtt

If there are any test failures, you will be shown the list of failures in a new
buffer. *Do not delete this buffer.* The code is new and can't handle that yet.

Advanced Usage
--------------

    :py sbt_init()

This will start the background SBT session without executing any SBT commands.

    :py sbt_close()

This will end the background session.

