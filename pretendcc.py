#!/bin/env python3
'''
a script that pretends to be a compiler, saves command line arguments, and passes them to the actual hardcoded compiler
'''

import subprocess
import os
import sys

def cmdline():
	return 'pretendcc ' + ' '.join(sys.argv[1:])

def main():
	invoke_cache_file = 'invkcache.txt'
	real_cc = 'gcc'
	with open(invoke_cache_file, 'a') as f:
		f.write(cmdline() + '\n')
	completed = subprocess.run(args=[real_cc, *sys.argv[1:]])
	sys.exit(completed.returncode)


if __name__ == '__main__':
	main()