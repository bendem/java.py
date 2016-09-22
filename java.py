#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import re
import subprocess
import sys
from time import perf_counter

pygments_available = True
try:
    import pygments
    from pygments.lexers import JavaLexer
    from pygments.formatters import TerminalFormatter
except ImportError:
    pygments_available = False

config = {
    'verbosity':  0,
    'pretty':     False,
    'setup':      [],
    'classpath':  [],
    'raw':        False,
    'java_args':  [],
    'bytecode':   False,
    'mvn':        [],
    'javac_args': ['-nowarn', '-encoding', 'utf-8'],
    'timings':    False,
    'debug':      False,
}

OUT        = os.path.join('/tmp' if os.name != 'nt' else os.getenv('temp'),
                          'java.py')
CLASS      = 'Paul%s' % int(random.random() * 100)
SOURCE     = '%s.java' % CLASS
COMPILED   = '%s.class' % CLASS
TEMPLATE   = """
import java.io.*;
import java.lang.reflect.*;
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
%s;

public class %s {
    private %s() {}

    public static void main(String[] args) throws Exception {
        %s;
        %s
    }

    private static void p(Object obj) {
        System.out.println(obj);
    }

    private static void p(String format, Object... params) {
        System.out.println(String.format(format, params));
    }

}
"""
OUTPUT_CODE_TEMPLATE = """
        Object ಠ_ಠ = %s;
        String ᴥ = "null";
        if(ಠ_ಠ != null) {
            if((ᴥ = ಠ_ಠ.getClass().getCanonicalName()) == null) {
                ᴥ = ಠ_ಠ.getClass().getName();
            }
            if(ᴥ.startsWith("java.lang.")) {
                ᴥ = ᴥ.substring("java.lang.".length());
            }
        }

        Stream<? extends Object> ϟ = null;
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
                .map(ツ -> String.format("%%s: %%s", ツ.getKey(), ツ.getValue()));

        } else if(ಠ_ಠ instanceof Stream<?>) {
            ϟ = (Stream<?>) ಠ_ಠ;

        } else if(ಠ_ಠ instanceof IntStream) {
            ϟ = ((IntStream) ಠ_ಠ).boxed();
        } else if(ಠ_ಠ instanceof LongStream) {
            ϟ = ((LongStream) ಠ_ಠ).boxed();
        } else if(ಠ_ಠ instanceof DoubleStream) {
            ϟ = ((DoubleStream) ಠ_ಠ).boxed();

        } else if(ಠ_ಠ instanceof Iterable<?>) {
            ϟ = StreamSupport.stream(((Iterable<?>) ಠ_ಠ).spliterator(), false);
        } else if(ಠ_ಠ instanceof Spliterator<?>) {
            ϟ = StreamSupport.stream((Spliterator<?>) ಠ_ಠ, false);
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
                    .collect((Collector<CharSequence, ?, String>) (%s
                        ? Collectors.joining(",\\n", "[\\n", "\\n]")
                        : Collectors.joining(", ", "[", "]")))
            );
        }
"""

def help():
    print('Usage is ./java.py [options] <code>')
    print()
    print('Options')
    print(' -b,   -bytecode   Prints the bytecode instead of executing the program (implies -r)')
    print(' -d,   -debug      Prints the code compiled and executed (requires pygments installed)')
    print(' -h,   -help       Prints this help message.')
    print(' -p,   -pretty     Pretty output(in case of program result convertible to stream, each item will be')
    print('                   printed on a new line).')
    print(' -r,   -raw        Prevents adding some code to display the result of the last operation')
    print('                   and replaces strip calls applied to each line of the program output with rstrip.')
    print(' -t,   -timing     Prints timing information about compilation and execution')
    print(' -v,   -verbose    Prints the commands used to compile and execute the script (provide this argument')
    print('                   twice if you want non-simplified commands).')
    print()
    print('Options with value')
    print(' -c,   -arg        Parameters to add to the java invocation')
    print(' -cp,  -classpath  Adds a jar to the classpath.')
    print(' -mvn, -maven      Adds maven dependencies of a project to the runtime classpath')
    print(' -s,   -setup      Setup code to put before the class declaration (i.e. imports or class definitions).')
    sys.exit()

def parse_args(args):
    code = []

    if len(args) == 1:
        help()

    arg_it = iter(args)
    next(arg_it)  # skip command

    for x in arg_it:
        if x == '-s' or x == '-setup':
            setup = next(arg_it)
            config['setup'] += setup.strip(';').split(';')
        elif x == '-p' or x == '-pretty':
            config['pretty'] = True
        elif x == '-v' or x == '-verbose':
            config['verbosity'] += 1
        elif x == '-vv':
            config['verbosity'] += 2
        elif x == '-r' or x == '-raw':
            config['raw'] = True
        elif x == '-cp' or x == '-classpath':
            config['classpath'].append(next(arg_it))
        elif x == '-h' or x == '-help' or x == '--help':
            help()
        elif x == '-c' or x == '-arg':
            config['java_args'].append(next(arg_it))
        elif x == '-b' or x == '-bytecode':
            config['bytecode'] = True
            config['raw'] = True
        elif x == '-mvn' or x == '-maven':
            config['mvn'].append(next(arg_it))
        elif x == '-t' or x == '-timing':
            config['timings'] = True
        elif x == '-d' or x == '-debug':
            config['debug'] = True
        else:
            code.append(x)

    if not code and not config['raw']:
        help()

    return code, config

def log(command):
    if not config['verbosity']:
        return

    if config['verbosity'] == 3:
        print(command)
        return

    if config['verbosity'] == 1:
        try:
            command = command.split(' ')
        except AttributeError:
            pass

        parts = []
        for part in command:
            if len(part) > 50:
                part = part[:20] + '[...]' + part[-20:]
            parts.append(part)
        command = ' '.join(parts)

    if not isinstance(command, str):
        command = ' '.join(command)

    print('%% %s' % command)

def generate_code(code, clazz, template, out_template=''):
    # Splitting on ; is really horrible and breaks in many cases but
    # it's a fair trade compared to the complexity of writing a parser
    code = code.strip(';').split(';')
    last_instr = code[-1].strip()
    output = ''

    if not config['raw']:
        output = out_template % (code[-1],
                ('true' if config['pretty'] else 'false'))
        del code[-1]

    return template % (';'.join(config['setup']), clazz, clazz,
            ';'.join(code), output)

def display_code(code):
    if not pygments_available:
        print('Warning: pygments not found')
        return

    print(pygments.highlight(code, JavaLexer(), TerminalFormatter()))

def write_to_file(file, content):
    dirname = os.path.dirname(file)
    if not os.path.exists(dirname):
        os.mkdir(dirname)

    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

def which(name):
    for path in os.getenv('PATH').split(os.pathsep):
        file = os.path.join(path, name)
        if os.path.isfile(file) and os.access(file, os.X_OK):
            return file

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

def read_stdin():
    return sys.stdin.readlines()

def exec(cmd, shell=True):
    log(cmd)
    return subprocess.Popen(cmd, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, universal_newlines=True,
            shell=shell, bufsize=1)

def find_maven_classpath(mvn):
    if not mvn:
        return []

    cp = []

    for folder in mvn:
        proc = exec(['mvn', 'dependency:build-classpath', '-f', folder], False)

        for line in proc.stdout:
            if line.startswith('[ERROR]') or line.startswith('[FATAL]'):
                print(line)
                break
            if not line.startswith('['):
                cp += line.strip().split(':')

    return cp

def compile(file, folder, java_home, javac_args, classpath):
    exe = '%s/bin/javac' % java_home
    args = list(javac_args)

    if classpath:
        args.append('-cp')
        args.append(':'.join(classpath))

    args.append('-d')
    args.append(folder)
    args.append(file)

    start = perf_counter()
    p = exec([exe] + args, False)

    for line in p.stdout:
        print('| %s' % line.rstrip())

    if p.wait() != 0:
        print('Compilation failed')
        cleanup(False)
        sys.exit(-1)
        return False

    if config['timings']:
        print('Program compiled in %f seconds' % (perf_counter() - start))

    return True

def run(clazz, bytecode, raw, java_home, java_args, classpath):
    exe = '%s/bin/java' % java_home
    cp = ':'.join(classpath + [OUT])
    args = java_args + ['-cp', cp]

    if bytecode:
        exe = '%s/bin/javap' % java_home
        args += ['-constants', '-package', '-c']
        if config['verbosity'] > 0:
            args.append('-v')

    args.append(clazz)

    start = perf_counter()
    execution = exec([exe] + args, False)

    if bytecode:
        # skip preamble
        for i in range(4 if config['verbosity'] > 0 else 1):
            execution.stdout.readline()

    for line in execution.stdout:
        if raw:
            line = line.rstrip()
        else:
            line = line.strip()
        print('>> %s' % line)

    execution.wait()

    if config['timings']:
        print('Program executed in %f seconds' % (perf_counter() - start))

def cleanup(compiled=True):
    os.remove('%s/%s' % (OUT, SOURCE))
    if compiled:
        os.remove('%s/%s' % (OUT, COMPILED))

if __name__ == '__main__':
    code_args, config = parse_args(sys.argv)

    if len(code_args) == 1 and code_args[0] == '-':
        code_args = read_stdin()

    java_home = find_java_home()
    if not java_home:
        print('| Java home not found, aborting...')
        sys.exit(1)

    code = generate_code(' '.join(code_args), CLASS,
            TEMPLATE, OUTPUT_CODE_TEMPLATE)

    if config['verbosity'] > 2:
        print(code)

    source = '%s/%s' % (OUT, SOURCE)

    if config['debug']:
        display_code(code)

    write_to_file(source, code)

    config['classpath'] += find_maven_classpath(config['mvn'])

    compiled = compile(source, OUT, java_home, config['javac_args'],
            config['classpath'])

    if compiled:
        run(CLASS, config['bytecode'], config['raw'], java_home,
                config['java_args'], config['classpath'])

    cleanup(source)
