
import display
import sbt

def handle_key(ch, name):
  if name == 'q':
    raise KeyboardInterrupt()
  elif name == 'c':
    sbt.compile()
  elif name == 't':
    sbt.test()

