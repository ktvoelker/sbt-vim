SBT-Vim Bridge
==============

This is a Vim plugin that allows [sbt](https://github.com/harrah/xsbt/wiki) to
be used from within [Vim](http://www.vim.org/).

Please [email me](mailto:sbt-vim@karlv.net) if you have questions.

Dependencies
------------

* Vim, compiled with support for Python 2 or 3 (check with `vim --version | grep -F +python`)
* SBT on your `$PATH` (check with `which sbt`)

Mac Homebrew users: if your Vim was built against Homebrew's Python, it probably won't work. To fix this:

    brew unlink python
    brew uninstall vim
    brew install homebrew/dupes/vim
    brew link python

Installation
------------

If you use [Pathogen](https://github.com/tpope/vim-pathogen), just clone this
repository in your `bundle` directory:

    git clone https://ktvoelker@github.com/ktvoelker/sbt-vim.git ~/.vim/bundle/sbt-vim

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
buffer named `sbt-vim-test` that you can delete any time.

Advanced Usage
--------------

    :py sbt_init()

This will start the background SBT session without executing any SBT commands.

    :py sbt_close()

This will end the background session.

