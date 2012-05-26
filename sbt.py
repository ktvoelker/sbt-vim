
import re
import subprocess
import uuid

from log import log

LINE_PADDING = 2
ERROR_HEADER = re.compile(r"(.+):(\d+): (.+)$")

class CompileError(object):

  def __init__(self, file=None, line=-1, col=-1, short=None, long=None, code=None):
    self.file = file
    self.line = line
    self.col = col
    self.short = short
    self.long = long
    self.code = code

  def jump_to(self):
    # TODO
    pass

def parse_chunk(lines):
  log("parse_chunk", lines=lines)
  n = len(lines)
  mo = re.match(ERROR_HEADER, lines[0])
  if not mo:
    return None
  file = mo.group(1)
  line = int(mo.group(2))
  short = mo.group(3).strip()
  long = None
  code = None
  col = None
  if lines[-1].strip() == "^" and n >= 3:
    code = lines[-2].strip()
    col = lines[-1].index("^") - LINE_PADDING + 1
    last_long_index = -3
  else:
    last_long_index = -1
  if abs(last_long_index) < n:
    long = "".join(lines[1, last_long_index])
  return CompileError(
      file=file,
      line=line,
      col=col,
      short=short,
      long=long,
      code=code)

def strip_error_tag(line):
  return line[len("[error] "):]

def line_is_error(line):
  return line.startswith("[error] ")

class Sbt(object):

  def __init__(self):
    pass

  def __enter__(self):
    self.proc = subprocess.Popen(
        ["sbt", "-Dsbt.log.noformat=true"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        close_fds=True)
    self.project_info = self.get_project_info()
    return self

  def __exit__(self, type, value, traceback):
    self.proc.stdin.close()
    self.proc.wait()

  def command(self, cmd):
    proc = self.proc
    marker = str(uuid.uuid4())
    log("command %s" % cmd)
    log("marker %s" % marker)
    proc.stdin.write(cmd)
    proc.stdin.write("\n")
    proc.stdin.write("eval print(\"%s\\n\")\n" % marker)
    lines = []
    line = proc.stdout.readline()
    log("discard line %s" % line)
    line = proc.stdout.readline()
    while line:
      log("got line %s" % line)
      if line.strip() == marker:
        log("found marker; read one more line")
        line = proc.stdout.readline()
        log("discard line %s" % line)
        break
      lines.append(line)
      line = proc.stdout.readline()
    log("done reading")
    return lines

  def get_project_info(self):
    name_line = self.proc.stdout.readline()
    log("name line %s" % name_line)
    lines = self.command("about")
    sbt_ver_line = lines[0]
    scala_ver_line = lines[2]
    ret = dict()
    name_mo = re.match(
        r"\[info\] Set current project to (.+) \(in build file:", name_line)
    log(name_mo=name_mo)
    if name_mo:
      ret['name'] = name_mo.group(1)
    else:
      ret['name'] = None
    sbt_ver_mo = re.match(
        r"\[info\] This is sbt ([\d\.]+)", sbt_ver_line)
    if sbt_ver_mo:
      ret['sbt_ver'] = sbt_ver_mo.group(1)
    else:
      ret['sbt_ver'] = None
    scala_ver_mo = re.match(
        r"\[info\] The current project is built against Scala ([\d\.]+)",
        scala_ver_line)
    if scala_ver_mo:
      ret['scala_ver'] = scala_ver_mo.group(1)
    else:
      ret['scala_ver'] = None
    return ret

  def compile(self):
    lines = map(strip_error_tag, filter(line_is_error, self.command("compile")))
    if len(lines) == 0:
      return []
    lines.reverse()
    chunks = []
    chunk = [lines.pop()]
    while len(lines) > 0:
      if lines[-1][0] == ' ':
        chunk.append(lines.pop())
      else:
        chunks.append(chunk)
        line = lines.pop()
        if line[0] != '/':
          break
        chunk = [line]
    return map(parse_chunk, chunks)

  def test(self):
    # TODO
    return []

