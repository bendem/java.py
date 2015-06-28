#!/usr/bin/python3
# -*- coding: utf-8 -*-

# TODO Support primitive arrays

import os
import subprocess
import sys

if len(sys.argv) == 1:
    print(' Plz, usage is ./java.py "<code>"')
    sys.exit()

setup = ''
arg_it = iter(sys.argv)
next(arg_it)
try:
    while True:
        x = next(arg_it)
        if x == '-s':
            setup = next(arg_it)
            sys.argv.remove(x)
            sys.argv.remove(setup)
            setup = setup.strip(';') + ';'
except StopIteration:
    pass

OUT      = '/tmp'
CLASS    = 'Paul'
SOURCE   = '%s.java' % CLASS
COMPILED = '%s.class' % CLASS

# something something backslash something
code = ' '.join(sys.argv[1:]).strip(';').replace('\\', '\\\\').split(';')
last_instr = code[-1].strip()
output = ''

# Auto display formatting thingy stuff
if not 'System.out.print' in last_instr and not last_instr.startswith('}'):
    output = """
        Object ಠ_ಠ = %s;
        Stream<?> ϟ = null;
        if(ಠ_ಠ instanceof Object[]) {
            ϟ = Arrays.stream((Object[]) ಠ_ಠ);

        } else if(ಠ_ಠ instanceof int[]) {
            ϟ = Arrays.stream((int[]) ಠ_ಠ).mapToObj(i -> Integer.valueOf(i));
        } else if(ಠ_ಠ instanceof long[]) {
            ϟ = Arrays.stream((long[]) ಠ_ಠ).mapToObj(i -> Long.valueOf(i));
        } else if(ಠ_ಠ instanceof double[]) {
            ϟ = Arrays.stream((double[]) ಠ_ಠ).mapToObj(i -> Double.valueOf(i));

        } else if(ಠ_ಠ instanceof Collection<?>) {
            ϟ = ((Collection<?>) ಠ_ಠ).stream();
        } else if(ಠ_ಠ instanceof Stream<?>) {
            ϟ = (Stream<?>) ಠ_ಠ;
        }

        if(ϟ == null) {
            System.out.println(ಠ_ಠ);
        } else {
            System.out.println(
                ϟ
                    .map(Object::toString)
                    .collect(Collectors.joining("', '", "['", "']"))
            );
        }
    """ % code[-1]
    del code[-1]

with open('%s/%s' % (OUT, SOURCE), 'w') as f:
    f.write(
        """
        import java.util.*;
        import java.util.stream.*;
        import java.math.*;
        import java.io.*;
        %s

        public class %s {
            public static void main(String[] args) throws Exception {
                %s;
                %s
            }
        }
        """ % (setup, CLASS, ';'.join(code), output)
    )

p = subprocess.Popen(
    'javac -nowarn -d %s %s/%s' % (OUT, OUT, SOURCE),
    shell = True,
    stdout = subprocess.PIPE,
    stderr = subprocess.STDOUT
)

for line in p.stdout.readlines():
    print(' | %s' % line.decode().strip())

if p.wait() != 0:
    print('Compilation failed')
    os.remove('%s/%s' % (OUT, SOURCE))
    sys.exit(-1)

execution = subprocess.Popen(
    'java -cp %s %s' % (OUT, CLASS),
    shell = True,
    stdout = subprocess.PIPE,
    stderr = subprocess.STDOUT
)

for line in execution.stdout.readlines():
    print(' >> %s' % line.decode().strip())

execution.wait()

os.remove('%s/%s' % (OUT, SOURCE))
os.remove('%s/%s' % (OUT, COMPILED))
