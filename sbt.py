
import re
import subprocess

from log import log

def get_project_info():
  about = subprocess.Popen(
      ["sbt", "about"],
      stdout=subprocess.PIPE,
      close_fds=True)
  name_line = about.stdout.readline().strip()
  sbt_ver_line = about.stdout.readline().strip()
  about.stdout.readline()
  scala_ver_line = about.stdout.readline().strip()
  while about.stdout.readline():
    pass
  about.wait()
  log(name_line)
  log(sbt_ver_line)
  log(scala_ver_line)
  ret = dict()
  name_mo = re.search(
      r"Set current project to (.+) \(in build file:", name_line)
  log(name_mo=name_mo)
  if name_mo:
    ret['name'] = name_mo.group(1)
  else:
    ret['name'] = None
  sbt_ver_mo = re.search(
      r"This is sbt ([\d\.]+)", sbt_ver_line)
  if sbt_ver_mo:
    ret['sbt_ver'] = sbt_ver_mo.group(1)
  else:
    ret['sbt_ver'] = None
  scala_ver_mo = re.search(
      r"The current project is built against Scala ([\d\.]+)", scala_ver_line)
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
  global project_info
  project_info = get_project_info()

def cleanup():
  pass

