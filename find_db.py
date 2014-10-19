#!/usr/bin/env python
import os

filenames = sorted(list(os.walk(os.getcwd()))[0][2])
centered = '\033[1;31m{:#^70}\033[0m'

for filename in filenames:
    if not filename.endswith('.py'):
        continue
    print centered.format('file: %s'%filename)
    f = open(filename)
    i = 0
    for line in f:
        i += 1
        line = line.strip()
        if line.startswith('def '):
            arg_start = line.find('(')
            if 'DB' in line[arg_start+1:]:
                print '\tline: \033[1;32m%d\033[0m'%i
                print '\tfunction sig: \033[1;34m%s\033[0m'%line
    f.close()
