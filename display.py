
import curses
import signal
import sys

next_color_pair = 1
def alloc_color_pair(fg, bg):
  global next_color_pair
  pair = next_color_pair
  next_color_pair += 1
  curses.init_pair(pair, fg, bg)
  return curses.color_pair(pair)

def handle_signal(sig, stack):
  cleanup()
  if sig == signal.SIGTERM:
    sys.exit(0)
  else:
    sys.exit(1)

def init():
  global root, title_bar, status_bar, content
  # Get the whole terminal as a Window object
  root = curses.initscr()
  curses.savetty()
  # Clean up the terminal if we get killed
  signal.signal(signal.SIGTERM, handle_signal)
  # Enable colors
  curses.start_color()
  # Get one character at a time
  curses.cbreak()
  curses.noecho()
  # Hide the cursor
  curses.curs_set(0)
  # Get the size of the terminal
  (h, w) = root.getmaxyx()
  # Make windows for the top and bottom bars
  title_bar = root.subwin(1, w, 0, 0)
  title_color = alloc_color_pair(curses.COLOR_WHITE, curses.COLOR_BLUE)
  title_bar.bkgdset(' ', curses.A_BOLD | title_color)
  title_bar.clear()
  # TODO put sbt version in title bar
  title_bar.insstr(0, 1, "csbt")
  status_bar = root.subwin(1, w, h - 1, 0)
  status_color = title_color
  status_bar.bkgdset(' ', status_color)
  status_bar.clear()
  status_bar.insstr(0, 1, "0 errors")
  # Make a window for the main content area
  content = root.subpad(h - 2, w, 1, 0)
  main_color = alloc_color_pair(curses.COLOR_BLACK, curses.COLOR_WHITE)
  content.bkgdset(' ', main_color)
  content.clear()

def run(handle_key):
  try:
    ch = root.getch()
    while ch >= 0:
      handle_key(ch, curses.keyname(ch))
      ch = root.getch()
  except KeyboardInterrupt:
    pass

def cleanup():
  curses.resetty()
  curses.endwin()

