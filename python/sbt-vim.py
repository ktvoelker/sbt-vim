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

  def _open_proc(self):
    return subprocess.Popen(
        ["sbt", "-Dsbt.log.noformat=true"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        close_fds=True)

  def __init__(self):
    self.buffer = None
    self.test_buffer = None
    self.proc = self._open_proc()

  class Buffer(object):

    def __init__(self, name="def"):
      full_name = "sbt-vim-%s" % name
      try:
        # check if our buffer exists already and reuse it
        vim.command("buffer %s" % full_name)
      except vim.error:
        # we need a new one
        vim.command("enew")
        vim.command("file %s" % full_name)
      self.buffer = vim.current.buffer
      # track if we may want to close quickfix window
      self.quickfix = False

    def delete(self):
      if self.buffer is not None:
        vim.command("bdelete " + self.buffer.name)

    def clear(self):
      # close quickfix if we opened it
      if self.quickfix:
          vim.command("cclose")
          vim.command("cexpr []")
          self.quickfix = False

      # There is a bug in vim 7.4, due to which this function was producing
      # an internal vim error. The problem seems to occur when the current
      # buffer is not our quickfix buffer, and the cursor position in the
      # current buffer is not a valid index into our quickfix buffer.
      prev_buffer = None
      if vim.current.buffer is not self.buffer:
          prev_buffer = vim.current.buffer
          vim.command("buffer %s" % self.buffer.name)
      del self.buffer[0:len(self.buffer)-1]
      if prev_buffer is not None:
          vim.command("buffer %s" % prev_buffer.name)

    def set_contents(self, lines, quickfix=False):
      if len(lines) > 0:
        self.buffer[0] = lines[0]
        self.buffer.append(lines[1:])
        if quickfix:
          vim.command("cbuffer %d" % self.buffer.number)
          # open the quickfix and remember to close it later
          vim.command("copen")
          self.quickfix = True

  def _init_buffer(self):
    if not self.buffer:
      # save current buffer name to go back to it
      prev = vim.current.buffer
      self.buffer = SBT.Buffer()
      vim.command("setlocal buftype=nofile")
      vim.command("setlocal bufhidden=hide")
      vim.command("setlocal noswapfile")
      vim.command("setlocal nobuflisted")
      # go back to the buffer
      vim.command("buffer %s" % prev.name)

  def _init_test_buffer(self):
    if not self.test_buffer:
      # save current buffer name to go back to it
      prev = vim.current.buffer
      self.test_buffer = SBT.Buffer("test")
      vim.command("setlocal buftype=nofile")
      vim.command("setlocal noswapfile")
      # go back to the buffer
      vim.command("buffer %s" % prev.name)

  def close(self):
    if self.buffer:
      self.buffer.delete()
    if self.test_buffer:
      self.test_buffer.delete()
    self.proc.stdin.close()
    self.proc.wait()

  def command(self, cmd, retry=True):
    to = self.proc.stdin
    send = lambda s: to.write(s.encode('utf-8'))
    fr = self.proc.stdout
    recv = lambda : fr.readline().decode('utf-8')

    marker = str(uuid.uuid4())

    send(cmd + '\n')
    send('eval print("{:s}\\n")\n'.format(marker))
    try:
      to.flush()
    except BrokenPipeError:
      if not retry:
          print("Failed to communicate with sbt")
          raise
      self.proc = self._open_proc()
      self.command(cmd, retry=False)
      return

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

