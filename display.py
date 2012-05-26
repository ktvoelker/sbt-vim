
import curses
import signal
import sys

from log import log
import sbt

HELP      = 1
ERROR     = 2
NO_ERRORS = 3

HELP_TEXT = """
    c  Compile          h  Next             e  Editor
    u  Test             t  Previous
    ?  Help             ^  First
    q  Quit             $  Last
"""

HAPPY = """
     ***   ***
      *     *

         >

   \~~~~~~~~~~~/
    \~~~~~~~~~/
"""

class Display(object):

  def __init__(self, sbt):
    log("init display", sbt=sbt)
    self.sbt = sbt
    self.next_color_pair = 1
    self.content_mode = HELP

  def handle_signal(self, sig, stack):
    if sig == signal.SIGTERM:
      sys.exit(0)
    else:
      sys.exit(1)

  def __enter__(self):
    # Get the whole terminal as a Window object
    self.root = curses.initscr()
    curses.savetty()
    # Clean up the terminal if we get killed
    signal.signal(signal.SIGTERM, lambda(sig, stack): self.handle_signal(sig, stack))
    # Enable colors
    curses.start_color()
    # Get one character at a time
    curses.cbreak()
    curses.noecho()
    # Hide the cursor
    curses.curs_set(0)
    # Get the size of the terminal
    (h, w) = self.root.getmaxyx()
    # Make windows for the top and bottom bars
    self.title_bar = self.root.subwin(1, w, 0, 0)
    self.init_title_bar()
    self.status_bar = self.root.subwin(1, w, h - 1, 0)
    self.status_color_good = self.alloc_color_pair(
        curses.COLOR_BLACK, curses.COLOR_GREEN)
    self.status_color_neutral = self.alloc_color_pair(
        curses.COLOR_WHITE, curses.COLOR_BLACK)
    self.status_color_bad = self.alloc_color_pair(
        curses.COLOR_WHITE, curses.COLOR_RED) | curses.A_BOLD
    # Make a window for the main content area
    self.content = self.root.subpad(h - 2, w, 1, 0)
    self.content_color_help = self.alloc_color_pair(
        curses.COLOR_BLACK, curses.COLOR_WHITE)
    self.content_color_data = self.alloc_color_pair(
        curses.COLOR_BLACK, curses.COLOR_WHITE)
    # Display the default content
    self.refresh()
    return self

  def __exit__(self, type, value, traceback):
    curses.resetty()
    curses.endwin()

  def alloc_color_pair(self, fg, bg):
    pair = self.next_color_pair
    self.next_color_pair += 1
    curses.init_pair(pair, fg, bg)
    return curses.color_pair(pair)

  def init_title_bar(self):
    title_color = self.alloc_color_pair(curses.COLOR_WHITE, curses.COLOR_BLUE)
    self.title_bar.bkgdset(' ', title_color)
    self.title_bar.clear()
    (h, w) = self.title_bar.getmaxyx()
    self.title_bar.addstr(" csbt 0.0.1    ")
    log(pi=self.sbt.project_info)
    self.title_bar.addstr("%s" % self.sbt.project_info['name'], curses.A_BOLD)
    ver_str = "sbt %s    scala %s " % (
        self.sbt.project_info['sbt_ver'], self.sbt.project_info['scala_ver'])
    self.title_bar.insstr(0, w - len(ver_str), ver_str)

  def run(self, control):
    try:
      ch = self.root.getch()
      while ch >= 0:
        control.handle_key(ch, curses.keyname(ch))
        ch = self.root.getch()
    except KeyboardInterrupt:
      pass

  def set_errors(self, errors):
    self.errors = errors
    if len(errors) > 0:
      self.error_index = 0
      self.content_mode = ERROR
    else:
      self.error_index = None
      self.content_mode = NO_ERRORS
    self.refresh()

  def show_help(self):
    self.content_mode = HELP
    self.refresh()

  def next_error(self):
    if self.content_mode == ERROR:
      self.error_index += 1
      if self.error_index == len(self.errors):
        self.error_index = 0
      self.refresh()

  def previous_error(self):
    if self.content_mode == ERROR:
      self.error_index -= 1
      if self.error_index < 0:
        self.error_index = len(self.errors) - 1
      self.refresh()

  def first_error(self):
    if self.content_mode == ERROR:
      self.error_index = 0
      self.refresh()

  def last_error(self):
    if self.content_mode == ERROR:
      self.error_index = len(self.errors)
      self.refresh()

  def set_colors(self, status, content):
    self.status_bar.bkgdset(' ', status)
    self.content.bkgdset(' ', content)
    self.status_bar.clear()
    self.content.clear()

  def current_error(self):
    if self.content_mode == ERROR:
      return self.errors[self.error_index]
    else:
      return None

  def refresh(self):
    if self.content_mode == HELP:
      self.set_colors(self.status_color_neutral, self.content_color_help)
      self.status_bar.insstr(0, 1, "Help")
      self.content.insstr(0, 0, HELP_TEXT)
    elif self.content_mode == ERROR:
      self.set_colors(self.status_color_bad, self.content_color_data)
      self.status_bar.insstr(0, 1, "%d errors" % len(self.errors))
      err = self.current_error()
      c = self.content
      c.insstr(1, 0, "%s" % err.file)
      if err.line and err.col:
        c.insstr(2, 0, "Line %d, Column %d" % (err.line, err.col))
      elif err.line:
        c.insstr(2, 0, "Line %d" % err.line)
      c.insstr(4, 0, "%s" % err.short)
      if err.long:
        c.insstr(6, 0, "%s" % err.long)
      (y, _) = c.getyx()
      c.insstr(y + 2, 4, "%s" % err.code)
      if err.code and err.col > 0:
        log("showing column pointer", y=y+2, x=err.col-1)
        c.insstr(y + 3, err.col + 3, "^")
    elif self.content_mode == NO_ERRORS:
      self.set_colors(self.status_color_good, self.content_color_data)
      self.status_bar.insstr(0, 1, "0 errors")
      self.content.insstr(4, 0, HAPPY)
    self.status_bar.refresh()
    self.content.refresh()

