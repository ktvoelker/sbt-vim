
let s:pysrc = expand("<sfile>:h") . "../python/sbt-vim.py"
pyfile s:pysrc

inoremap sbtc py sbt_compile()
inoremap sbtt py sbt_test()

