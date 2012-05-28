
import re
import subprocess
import uuid
import vim

class SBT(object):

  def __init__(self):
    self.buffer = None
    self.bufnum = None
    self.test_buffer = None
    self.test_bufnum = None
    self.proc = subprocess.Popen(
        ["sbt", "-Dsbt.log.noformat=true"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        close_fds=True)

  # TODO move the huge amount of per-buffer logic into an inner Buffer class
  def _new_buffer(self):
    vim.command("enew")
    for i in xrange(0, len(vim.buffers)):
      if vim.buffers[i] == vim.current.buffer:
        bufnum = i + 1
        break
    if bufnum is None:
      raise RuntimeError("Couldn't find buffer in buffers array.")
    return (bufnum, vim.current.buffer)

  def _delete_buffer(self, bufnum, buffer):
    if bufnum is not None and buffer is not None:
      if vim.buffers[bufnum] is buffer:
        vim.command("bdelete " + bufnum)

  def _init_buffer(self):
    if not self.buffer:
      (self.bufnum, self.buffer) = self._new_buffer()
      vim.command("setlocal buftype=nofile")
      vim.command("setlocal bufhidden=hide")
      vim.command("setlocal noswapfile")
      vim.command("setlocal nobuflisted")
      # TODO go back to the last buffer that was open
      if self.bufnum > 1:
        vim.command("bprevious")

  def _init_test_buffer(self):
    if not self.test_buffer:
      (self.test_bufnum, self.test_buffer) = self._new_buffer()
      vim.command("setlocal buftype=nofile")
      vim.command("setlocal noswapfile")
      # TODO name the buffer

  def close(self):
    self._delete_buffer(self, self.bufnum, self.buffer)
    self._delete_buffer(self, self.test_bufnum, self.test_buffer)
    self.proc.stdin.close()
    self.proc.wait()

  def command(self, cmd):
    to = self.proc.stdin
    fr = self.proc.stdout
    marker = str(uuid.uuid4())
    to.write(cmd)
    to.write("\n")
    to.write("eval print(\"%s\\n\")\n" % marker)
    fr.readline()
    line = fr.readline()
    while line:
      if line.strip() == marker:
        fr.readline()
        break
      yield line
      line = fr.readline()

  ERROR_TAG = "[error] "
  ERROR_TAG_LEN = len(ERROR_TAG)

  def _filter_errors(self, lines):
    for line in lines:
      if line.startswith(SBT.ERROR_TAG):
        yield line[SBT.ERROR_TAG_LEN:]

  def _filter_files(self, lines):
    for line in lines:
      if line.startswith("/"):
        yield line[1:]

  def _clear_buffer(self, buffer):
    del buffer[:]

  def _set_buffer_contents(self, buffer, lines):
    buffer[0] = lines[0]
    buffer.append(lines[1:])

  def _set_compile_errors(self, errors):
    self._set_buffer_contents(self.buffer, errors)
    vim.command("cbuffer %d" % self.bufnum)

  def compile(self):
    self._init_buffer()
    self._clear_buffer(self.buffer)
    lines = list(self._filter_files(self._filter_errors(self.command("compile"))))
    if len(lines) > 0:
      self._set_compile_errors(lines)
    else:
      print("No errors.")

  def test(self):
    self._init_buffer()
    self._clear_buffer(self.buffer)
    lines = list(self._filter_errors(self.command("test")))
    if len(lines) > 0:
      files = list(self._filter_files(lines))
      if len(files) > 0:
        self._set_compile_errors(files)
      else:
        # TODO print the number of tests with each status
        self._init_test_buffer()
        self._clear_buffer(self.test_buffer)
        self._set_buffer_contents(self.test_buffer, lines)
    else:
      # TODO print the number of tests with each status
      print("No errors.")

sbt = None

def sbt_init():
  global sbt
  if not sbt:
    sbt = SBT()

def sbt_compile():
  global sbt
  sbt_init()
  sbt.compile()

def sbt_test():
  global sbt
  sbt_init()
  sbt.test()

