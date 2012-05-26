
SBT + VIM
=========

Make a wrapper around SBT that runs "~ compile" or "~ test", parses the output,
and writes error locations to a file in an easily-parsed format. The wrapper
should also present the output nicely on the console: it should take over the
console and show the current error message with plenty of nice whitespace
around it.  If necessary, it should make the message scrollable. Below that, it
can show further errors, but all but the first should be less bold.

The error location file only contains the location of the currently-selected
error.

Make a vim command that can read that file and go to the error location.

There should also be a command in the SBT wrapper that can open the error
location in whatever vim process already has that file open. Use lsof to find
the process.  How do we signal that process? If there isn't already an open vim
process, the SBT wrapper can just open vim on its own console. When you quit
vim, it goes to the next error.

Vim seems to have a client/server system that allows it to be sent commands remotely.
This will be useful.

