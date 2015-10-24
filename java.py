#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import subprocess
import sys

verbose   = False
pretty    = False
setup     = ''
classpath = []
code_args = []

javac_args = ''
java_args  = ''
OUT        = '/tmp'
CLASS      = 'Paul'
SOURCE     = '%s.java' % CLASS
COMPILED   = '%s.class' % CLASS
TEMPLATE   = """
    import java.io.*;
    import java.math.*;
    import java.nio.*;
    import java.nio.charset.*;
    import java.nio.file.*;
    import java.time.*;
    import java.time.chrono.*;
    import java.time.format.*;
    import java.time.temporal.*;
    import java.time.zone.*;
    import java.util.*;
    import java.util.concurrent.*;
    import java.util.concurrent.atomic.*;
    import java.util.concurrent.locks.*;
    import java.util.function.*;
    import java.util.stream.*;
    %s

    public class %s {
        public static void main(String[] args) throws Exception {
            %s;
            %s
        }
    }
    """
OUTPUT_CODE_TEMPLATE = """
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
"""

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

def parse_args(args):
    global verbose, pretty, setup, classpath, code_args

    if len(args) == 1:
        help()

    arg_it = iter(args)
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

    if not code_args:
        help()

def generate_code(code):
    # Splitting on ; is really horrible and breaks in many cases but
    # it's a fair trade compared to the complexity of writing a parser
    code = code.strip(';').split(';')
    last_instr = code[-1].strip()
    output = ''

    if '=' in last_instr:
        to_print = last_instr.split('=')[0].strip()

        # Extracts var name from declarations like "int a"
        # or "Map<String, String> a"
        if ' ' in to_print:
            r = re.compile(r'^.+\s+([^ ]+)$').match(to_print).group(1)
            to_print = ' '.join(r)

        code.append(to_print)
        last_instr = to_print

    # Auto display formatting thingy stuff
    if not 'print' in last_instr and not last_instr.endswith('}'):
        output = OUTPUT_CODE_TEMPLATE % (code[-1], ('\\n' if pretty else ' '))
        del code[-1]

    return TEMPLATE % (setup, CLASS, ';'.join(code), output)

def write_to_file(code, file):
    # with open('%s/%s' % (OUT, SOURCE), 'w') as f:
    with open(file, 'w') as f:
        f.write(code)

def compile():
    args = javac_args + ' -nowarn'
    if classpath:
        args += ' -cp %s' % ':'.join(classpath)

    javac = 'javac %s -d %s %s/%s' % (args, OUT, OUT, SOURCE)
    javac = javac.replace('  ', ' ')

    if verbose:
        print('%% %s' % javac)

    p = subprocess.Popen(javac, shell = True, stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT)

    for line in p.stdout.readlines():
        print(' | %s' % line.decode().strip())

    if p.wait() != 0:
        print('Compilation failed')
        cleanup(False)
        sys.exit(-1)
        return False

    return True

def run():
    args = java_args + ' -cp %s' % ':'.join(classpath + [OUT])
    java = 'java %s %s' % (args, CLASS)
    java = java.replace('  ', ' ')

    if verbose:
        print('%% %s' % java)

    execution = subprocess.Popen(java, shell = True, stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT)

    for line in execution.stdout.readlines():
        print(' >> %s' % line.decode().strip())

    execution.wait()

def cleanup(compiled = True):
    os.remove('%s/%s' % (OUT, SOURCE))
    if compiled:
        os.remove('%s/%s' % (OUT, COMPILED))

if __name__ == '__main__':
    parse_args(sys.argv)
    code = generate_code(' '.join(code_args))
    write_to_file(code, '%s/%s' % (OUT, SOURCE))
    if compile():
        run()
        cleanup()
