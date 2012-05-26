
import sys
import time

enable = True
ready = False
out = None

def init():
  global enable, ready, out
  if enable and not ready:
    out = open('log.txt', 'a')
    if not out:
      out = sys.stderr
    if out:
      log('Begin logging.', time=time.ctime())
    ready = True

def log(*stuff, **kv):
  global out
  if out:
    if len(stuff) > 0:
      out.write(" ".join(map(str, stuff)))
      out.write("\n")
    if len(kv) > 0:
      for k in kv:
        out.write("    %s: %r\n" % (k, kv[k]))
    out.flush()

def cleanup():
  global out
  if out:
    out.close()
