"""
run.py

A simple Egor runner, for quick access.
"""

try:
	from . import egor
except ImportError:
	import os
	import sys
	here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	sys.path.insert(0, here)
	from dm import egor

def run():
	interface = egor.Egor()
	interface.cmdloop()
	return interface

if __name__ == '__main__':
	run()