#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import subprocess
import sys

verbose   = False
pretty    = False
raw       = False
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
    import java.security.*;
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
    import java.util.regex.*;
    import java.util.stream.*;
    import javax.crypto.*;
    import javax.crypto.spec.*;
    %s

    public class %s {
        public static void main(String[] args) throws Exception {
            %s;
            %s
        }

        public static void p(Object obj) {
            System.out.println(obj.toString());
        }

        public static void p(String format, Object... params) {
            System.out.println(String.format(format, params));
        }

    }
    """
OUTPUT_CODE_TEMPLATE = """
    Object ಠ_ಠ = %s;
    String ᴥ = "null";
    if(ಠ_ಠ != null) {
        if(ಠ_ಠ.getClass().getName().startsWith("java.lang.")) {
            ᴥ = ಠ_ಠ.getClass().getSimpleName();
        } else {
            ᴥ = ಠ_ಠ.getClass().getName();
        }
    }

    Stream<?> ϟ = null;
    if(ಠ_ಠ instanceof Object[]) {
        ϟ = Arrays.stream((Object[]) ಠ_ಠ);

    } else if(ಠ_ಠ instanceof int[]) {
        ϟ = Arrays.stream((int[]) ಠ_ಠ).mapToObj(Integer::valueOf);
    } else if(ಠ_ಠ instanceof long[]) {
        ϟ = Arrays.stream((long[]) ಠ_ಠ).mapToObj(Long::valueOf);
    } else if(ಠ_ಠ instanceof double[]) {
        ϟ = Arrays.stream((double[]) ಠ_ಠ).mapToObj(Double::valueOf);

    } else if(ಠ_ಠ instanceof Map<?, ?>) {
        ϟ = ((Map<?, ?>) ಠ_ಠ).entrySet().stream()
            .map(e -> String.format("%%s: %%s", e.getKey(), e.getValue()));

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
        System.out.println("(" + ᴥ + ") " + ಠ_ಠ);
    } else {
        System.out.printf("(" + ᴥ + ") ");
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
    print()
    print(' Usage is ./java.py [options] <code>')
    print()
    print(' Options are:')
    print()
    print('    -p  Pretty output (in case of program result convertible to stream, each item will be printed on a new line).')
    print()
    print('    -s  Setup code to put before the class declaration (i.e. imports or class definitions).')
    print()
    print('    -h  Prints this help message.')
    print()
    print('    -v  Prints the commands used to compile and execute the script.')
    print()
    print('    -r  Prevents adding some code to display the result of the last operation and replaces strip calls applied')
    print('        to each line of the program output with rstrip.')
    print()
    print('    -cp Adds a jar to the classpath.')
    print()
    print('    -c Parameters to add to the java invocation')
    print()
    sys.exit()

def parse_args(args):
    global verbose, pretty, setup, classpath, code_args, raw, java_args

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
            elif x == '-r':
                raw = True
            elif x == '-cp':
                classpath.append(next(arg_it))
            elif x == '-h' or x == '--help':
                help()
            elif x == '-c':
                java_args = next(arg_it)
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

    if not raw and '=' in last_instr:
        to_print = last_instr.split('=')[0].strip()

        # Extracts var name from declarations like "int a"
        # or "Map<String, String> a"
        if ' ' in to_print:
            r = re.compile(r'^.+\s+([^ ]+)$').match(to_print).group(1)
            to_print = ' '.join(r)

        code.append(to_print)
        last_instr = to_print

    # Auto display formatting thingy stuff
    if not raw \
            and not last_instr.startswith('p(') \
            and not last_instr.endswith('}'):
        output = OUTPUT_CODE_TEMPLATE % (code[-1], ('\\n' if pretty else ' '))
        del code[-1]

    return TEMPLATE % (setup, CLASS, ';'.join(code), output)

def write_to_file(code, file):
    with open(file, 'w') as f:
        f.write(code)

def which(name):
    for path in os.getenv('PATH').split(os.pathsep):
        file = os.path.join(path, name)
        if os.path.isfile(file) and os.access(file, os.X_OK):
            return file

    return None

def dirname(name, count):
    for i in range(count):
        name = os.path.dirname(name)

    return name

def find_java_home():
    java_home = os.getenv('JAVA_HOME')
    if java_home:
        return java_home

    java_home = which('javac')
    if java_home:
        return dirname(java_home, 2)

    return None

def compile(javac):
    args = javac_args + ' -nowarn'
    if classpath:
        args += ' -cp %s' % ':'.join(classpath)

    javac = '%s %s -d %s %s/%s' % (javac, args, OUT, OUT, SOURCE)
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

def run(java):
    cp = ':'.join(classpath + [OUT])
    args = '%s -cp %s' % (java_args, cp)
    java = '%s %s %s' % (java, args, CLASS)
    java = java.replace('  ', ' ')

    if verbose:
        print('%% %s' % java)

    execution = subprocess.Popen(java, shell = True, stdout = subprocess.PIPE,
        stderr = subprocess.STDOUT)

    for line in execution.stdout.readlines():
        l = line.decode()
        if raw:
            l = l.rstrip()
        else:
            l = l.strip()
        print(' >> %s' % l)

    execution.wait()

def cleanup(compiled = True):
    os.remove('%s/%s' % (OUT, SOURCE))
    if compiled:
        os.remove('%s/%s' % (OUT, COMPILED))

if __name__ == '__main__':
    parse_args(sys.argv)
    java_home = find_java_home()
    if not java_home:
        print(' Java home not found, aborting...')
        os.exit(1)

    code = generate_code(' '.join(code_args))
    write_to_file(code, '%s/%s' % (OUT, SOURCE))
    if compile('%s/bin/javac' % java_home):
        run('%s/bin/java' % java_home)
        cleanup()
