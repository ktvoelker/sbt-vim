" Copyright 2012 Karl Voelker <ktvoelker@gmail.com>
"
" This file is part of SBT-Vim.
" 
" SBT-Vim is free software: you can redistribute it and/or modify
" it under the terms of the GNU General Public License as published by
" the Free Software Foundation, either version 3 of the License, or
" (at your option) any later version.
" 
" SBT-Vim is distributed in the hope that it will be useful,
" but WITHOUT ANY WARRANTY; without even the implied warranty of
" MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
" GNU General Public License for more details.
" 
" You should have received a copy of the GNU General Public License
" along with SBT-Vim.  If not, see <http://www.gnu.org/licenses/>.

" TODO warn the user (and do nothing else) if Python is not supported
let s:pysrc = expand("<sfile>:h") . "/../python/sbt-vim.py"
exec "pyfile" s:pysrc

cab sbtc py sbt_compile()
cab sbtt py sbt_test()

