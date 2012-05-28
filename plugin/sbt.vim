
" TODO add copyright header

" TODO warn the user (and do nothing else) if Python is not supported
let s:pysrc = expand("<sfile>:h") . "/../python/sbt-vim.py"
exec "pyfile" s:pysrc

cab sbtc py sbt_compile()
cab sbtt py sbt_test()

