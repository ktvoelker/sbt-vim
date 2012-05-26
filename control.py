
import display
import sbt

class Control(object):

  def __init__(self, display=None, sbt=None):
    self.display = display
    self.sbt = sbt

  def handle_key(self, ch, name):
    if name == "q":
      raise KeyboardInterrupt()
    elif name == "c":
      self.display.set_errors(self.sbt.compile())
    elif name == "u":
      self.display.set_errors(self.sbt.test())
    elif name == "?":
      self.display.show_help()
    elif name == "h":
      self.display.next_error()
    elif name == "t":
      self.display.previous_error()
    elif name == "^":
      self.display.first_error()
    elif name == "$":
      self.display.last_error()
    elif name == "\n":
      err = self.current_error()
      if err:
        err.jump_to()

