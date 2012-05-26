
import curses
import signal
import sys

from log import log
import sbt

class Display(object):

  def __init__(self, sbt):
    log("init display", sbt=sbt)
    self.sbt = sbt
    self.next_color_pair = 1

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
    status_color = self.alloc_color_pair(curses.COLOR_BLACK, curses.COLOR_GREEN)
    self.status_bar.bkgdset(' ', status_color)
    self.status_bar.clear()
    self.status_bar.insstr(0, 1, "0 errors")
    # Make a window for the main content area
    self.content = self.root.subpad(h - 2, w, 1, 0)
    main_color = self.alloc_color_pair(curses.COLOR_BLACK, curses.COLOR_WHITE)
    self.content.bkgdset(' ', main_color)
    self.content.clear()
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

  def run(self, handle_key):
    try:
      ch = self.root.getch()
      while ch >= 0:
        handle_key(ch, curses.keyname(ch))
        ch = self.root.getch()
    except KeyboardInterrupt:
      pass

