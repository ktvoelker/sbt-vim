# Copyright 2012-2014 Karl Voelker <sbt-vim@karlv.net>
#
# This file is part of SBT-Vim.
# 
# SBT-Vim is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# SBT-Vim is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with SBT-Vim.  If not, see <http://www.gnu.org/licenses/>.

import re
import subprocess
import uuid
import vim

class SBT(object):

  def __init__(self):
    self.buffer = None
    self.test_buffer = None
    self.proc = subprocess.Popen(
        ["sbt", "-Dsbt.log.noformat=true"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        close_fds=True)

  class Buffer(object):

    def __init__(self):
      vim.command("enew")
      self.buffer = vim.current.buffer

    def delete(self):
      if self.buffer is not None:
        vim.command("bdelete " + self.buffer.number)

    def clear(self):
      # There is a bug in vim 7.4, due to which this function was producing
      # an internal vim error. The problem seems to occur when the current
      # buffer is not our quickfix buffer, and the cursor position in the
      # current buffer is not a valid index into our quickfix buffer.
      prev_buffer = None
      if vim.current.buffer is not self.buffer:
          prev_buffer = vim.current.buffer
          vim.command("buffer %d" % self.buffer.number)
      del self.buffer[0:len(self.buffer)-1]
      if prev_buffer is not None:
          vim.command("buffer %d" % prev_buffer.number)

    def set_contents(self, lines, quickfix=False):
      if len(lines) > 0:
        self.buffer[0] = lines[0]
        self.buffer.append(lines[1:])
        if quickfix:
          vim.command("cbuffer %d" % self.buffer.number)

    def go_previous(self):
      # TODO go back to the last buffer that was open
      if self.buffer.number > 1:
        vim.command("bprevious")

  def _init_buffer(self):
    # TODO figure out if the user deleted this buffer
    if not self.buffer:
      self.buffer = SBT.Buffer()
      vim.command("setlocal buftype=nofile")
      vim.command("setlocal bufhidden=hide")
      vim.command("setlocal noswapfile")
      vim.command("setlocal nobuflisted")
      # TODO name the buffer
      self.buffer.go_previous()

  def _init_test_buffer(self):
    # TODO figure out if the user deleted this buffer
    if not self.test_buffer:
      self.test_buffer = SBT.Buffer()
      vim.command("setlocal buftype=nofile")
      vim.command("setlocal noswapfile")
      # TODO name the buffer

  def close(self):
    if self.buffer:
      self.buffer.delete()
    if self.test_buffer:
      self.test_buffer.delete()
    self.proc.stdin.close()
    self.proc.wait()

  def command(self, cmd):
    to = self.proc.stdin
    send = lambda s: to.write(s.encode('utf-8'))
    fr = self.proc.stdout
    recv = lambda : fr.readline().decode('utf-8')

    marker = str(uuid.uuid4())

    send(cmd + '\n')
    send('eval print("{:s}\\n")\n'.format(marker))
    to.flush()

    while True:
      line = recv()
      if not line:
        continue
      if line.strip() == marker:
        break
      yield line

  ERROR_TAG = "[error] "
  ERROR_TAG_LEN = len(ERROR_TAG)

  def _filter_errors(self, lines):
    for line in lines:
      if line.startswith(SBT.ERROR_TAG):
        yield line[SBT.ERROR_TAG_LEN:]

  def _filter_files(self, lines):
    for line in lines:
      if line.startswith("/"):
        yield line

  def _set_compile_errors(self, errors):
    self.buffer.set_contents(errors, quickfix=True)

  def compile(self):
    self._init_buffer()
    self.buffer.clear()
    lines = list(self._filter_files(self._filter_errors(self.command("compile"))))
    if len(lines) > 0:
      self._set_compile_errors(lines)
    else:
      print("No errors.")

  def test(self):
    self._init_buffer()
    self.buffer.clear()
    lines = list(self._filter_errors(self.command("test")))
    if len(lines) > 0:
      files = list(self._filter_files(lines))
      if len(files) > 0:
        self._set_compile_errors(files)
      else:
        # TODO print the number of tests with each status
        self._init_test_buffer()
        self.test_buffer.clear()
        self.test_buffer.set_contents(lines)
    else:
      # TODO print the number of tests with each status
      print("No errors.")

sbt = None

def sbt_init():
  global sbt
  if not sbt:
    sbt = SBT()

def sbt_close():
  global sbt
  if sbt:
    sbt.close()
    sbt = None

def sbt_compile():
  global sbt
  sbt_init()
  sbt.compile()

def sbt_test():
  global sbt
  sbt_init()
  sbt.test()

