
import re
import subprocess
import uuid

from log import log

proc = None
project_info = None

def command(cmd):
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

def get_project_info():
  name_line = proc.stdout.readline()
  log("name line %s" % name_line)
  lines = command("about")
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

def compile():
  pass

def test():
  pass

def init():
  global proc, project_info
  proc = subprocess.Popen(
      ["sbt", "-Dsbt.log.noformat=true"],
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      close_fds=True)
  project_info = get_project_info()

def cleanup():
  proc.stdin.close()
  proc.wait()

