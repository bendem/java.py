#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys

def help():
    print(' Usage is ./java.py [options] <code>')
    print()
    print(' Options are:')
    print('    -p  Pretty output')
    print('    -s  Setup code to put before the class declaration (i.e. imports)')
    print('    -h  Prints this help message')
    print('    -v  Prints the commands used to compile and execute the script')
    print('    -cp Adds a jar to the classpath')
    sys.exit()

if len(sys.argv) == 1:
    help()

verbose   = False
pretty    = False
setup     = ''
classpath = []
code_args = []

arg_it = iter(sys.argv)
next(arg_it)
try:
    while True:
        x = next(arg_it)
        if x == '-s':
            setup = next(arg_it)
            setup = setup.strip(';') + ';'
        elif x == '-p':
            pretty = True
        elif x == '-v':
            verbose = True
        elif x == '-cp':
            classpath.append(next(arg_it))
        elif x == '-h' or x == '--help':
            help()
        else:
            code_args.append(x)
except StopIteration:
    pass

OUT        = '/tmp'
CLASS      = 'Paul'
SOURCE     = '%s.java' % CLASS
COMPILED   = '%s.class' % CLASS
javac_args = ''
java_args  = ''

# something something backslash something
code = ' '.join(code_args).strip(';').replace('\\', '\\\\').split(';')
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
            ϟ = Arrays.stream((int[]) ಠ_ಠ).mapToObj(Integer::valueOf);
        } else if(ಠ_ಠ instanceof long[]) {
            ϟ = Arrays.stream((long[]) ಠ_ಠ).mapToObj(Long::valueOf);
        } else if(ಠ_ಠ instanceof double[]) {
            ϟ = Arrays.stream((double[]) ಠ_ಠ).mapToObj(Double::valueOf);

        } else if(ಠ_ಠ instanceof Collection<?>) {
            ϟ = ((Collection<?>) ಠ_ಠ).stream();
        } else if(ಠ_ಠ instanceof Stream<?>) {
            ϟ = (Stream<?>) ಠ_ಠ;

        } else if(ಠ_ಠ instanceof IntStream) {
            ϟ = ((IntStream) ಠ_ಠ).boxed();
        } else if(ಠ_ಠ instanceof LongStream) {
            ϟ = ((LongStream) ಠ_ಠ).boxed();
        } else if(ಠ_ಠ instanceof DoubleStream) {
            ϟ = ((DoubleStream) ಠ_ಠ).boxed();
        }

        if(ϟ == null) {
            System.out.println(ಠ_ಠ);
        } else {
            System.out.println(
                ϟ
                    .map(ツ -> {
                        if(ツ == null) {
                            return "null";
                        }
                        if(ツ instanceof Character) {
                            return "'" + ツ + "'";
                        }
                        if(ツ instanceof Number) {
                            return ツ.toString();
                        }
                        return "\\"" + ツ + '"';
                    })
                    .collect(Collectors.joining(",%s", "[", "]"))
            );
        }
    """ % (code[-1], ('\\n' if pretty else ' '))
    del code[-1]

with open('%s/%s' % (OUT, SOURCE), 'w') as f:
    f.write(
        """
        import java.io.*;
        import java.math.*;
        import java.util.*;
        import java.util.stream.*;
        %s

        public class %s {
            public static void main(String[] args) throws Exception {
                %s;
                %s
            }
        }
        """ % (setup, CLASS, ';'.join(code), output)
    )

javac_args += ' -nowarn'
if classpath:
    javac_args += ' -cp %s' % ':'.join(classpath)

javac = 'javac %s -d %s %s/%s' % (javac_args, OUT, OUT, SOURCE)

if verbose:
    print('%% %s' % javac.replace('  ', ' '))

p = subprocess.Popen(javac, shell = True, stdout = subprocess.PIPE,
    stderr = subprocess.STDOUT)

for line in p.stdout.readlines():
    print(' | %s' % line.decode().strip())

if p.wait() != 0:
    print('Compilation failed')
    os.remove('%s/%s' % (OUT, SOURCE))
    sys.exit(-1)


java_args += ' -cp %s' % ':'.join(classpath + [OUT])
java = 'java %s %s' % (java_args, CLASS)

if verbose:
    print('%% %s' % java.replace('  ', ' '))

execution = subprocess.Popen(java, shell = True, stdout = subprocess.PIPE,
    stderr = subprocess.STDOUT)

for line in execution.stdout.readlines():
    print(' >> %s' % line.decode().strip())

execution.wait()

os.remove('%s/%s' % (OUT, SOURCE))
os.remove('%s/%s' % (OUT, COMPILED))
