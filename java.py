#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import subprocess
import sys

verbosity = 0
pretty    = False
raw       = False
setup     = ''
bytecode  = False
classpath = []
code_args = []
mvn       = ''

javac_args = ''
java_args  = ''
OUT        = '/tmp'
CLASS      = 'Paul'
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
    %s

    public class %s {
        private %s() {}

        public static void main(String[] args) throws Exception {
            %s;
            %s
        }

        private static void p(Object obj) {
            System.out.println(obj.toString());
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
        ᴥ = ಠ_ಠ.getClass().getCanonicalName();
        if(ᴥ.startsWith("java.lang.")) {
            ᴥ = ᴥ.substring("java.lang.".length());
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
    print()
    print('Usage is ./java.py [options] <code>')
    print()
    print('Options are:')
    print()
    print('    -b   Prints the bytecode instead of executing the program (implies -r)')
    print('    -c   Parameters to add to the java invocation')
    print('    -cp  Adds a jar to the classpath.')
    print('    -h   Prints this help message.')
    print('    -mvn Adds maven dependencies of a project to the runtime classpath')
    print('    -p   Pretty output(in case of program result convertible to stream, each item will be printed on a new line).')
    print('    -r   Prevents adding some code to display the result of the last operation and replaces strip calls applied to each line of the program output with rstrip.')
    print('    -s   Setup code to put before the class declaration (i.e. imports or class definitions).')
    print('    -v   Prints the commands used to compile and execute the script (provide this argument twice if you want non-simplified commands).')
    print()
    sys.exit()

def parse_args(args):
    global verbosity, pretty, setup, classpath, code_args, raw, java_args, bytecode, mvn

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
                verbosity += 1
            elif x == '-r':
                raw = True
            elif x == '-cp':
                classpath.append(next(arg_it))
            elif x == '-h' or x == '--help':
                help()
            elif x == '-c':
                java_args = next(arg_it)
            elif x == '-b':
                bytecode = True
                raw = True
            elif x == '-mvn':
                mvn = next(arg_it)
            else:
                code_args.append(x)
    except StopIteration:
        pass

    if not code_args and not raw:
        help()

def log(command):
    if verbosity == 0:
        return

    if verbosity == 1:
        if not isinstance(command, list):
            command = command.split(' ')

        parts = []
        for part in command:
            if len(part) > 50:
                part = part[:20] + '[...]' + part[-20:]
            parts.append(part)
        command = ' '.join(parts)

    if isinstance(command, list):
        command = ' '.join(command)

    print('%% %s' % command)

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
            and not last_instr == '}':
        output = OUTPUT_CODE_TEMPLATE % (code[-1], ('true' if pretty else 'false'))
        del code[-1]

    return TEMPLATE % (setup, CLASS, CLASS, ';'.join(code), output)

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

def read_stdin():
    return sys.stdin.readlines()

def exec(cmd, shell = True):
    log(cmd)
    return subprocess.Popen(cmd, stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT, universal_newlines = True,
            shell = shell, bufsize = 1)

def find_maven_classpath(mvn):
    if not mvn:
        return []

    proc = exec(['mvn', 'dependency:build-classpath', '-f', mvn], False)

    for line in proc.stdout:
        if line.startswith('[ERROR]') or line.startswith('[FATAL]'):
            print(line)
            break
        if not line.startswith('['):
            return line.strip().split(':')

    print('| mvn exited with status %s' % proc.wait())

    return []

def compile(java_home, classpath):
    javac = '%s/bin/javac' % java_home
    args = javac_args + ' -nowarn'
    if classpath:
        args += ' -cp %s' % ':'.join(classpath)

    javac = '%s %s -d %s %s/%s' % (javac, args, OUT, OUT, SOURCE)
    javac = javac.replace('  ', ' ')

    p = exec(javac)

    for line in p.stdout:
        print('| %s' % line.rstrip())

    if p.wait() != 0:
        print('Compilation failed')
        cleanup(False)
        sys.exit(-1)
        return False

    return True

def run(java_home, classpath):
    cp = ':'.join(classpath + [OUT])
    args = '%s -cp %s' % (java_args, cp)
    if bytecode:
        if verbosity > 0:
            args += ' -v'
        cmd = '%s/bin/javap -constants -package -c %s %s' % (java_home, args, CLASS)
    else:
        cmd = '%s/bin/java %s %s' % (java_home, args, CLASS)

    cmd = cmd.replace('  ', ' ')

    execution = exec(cmd)

    if bytecode:
        # skip preamble
        [execution.stdout.readline() for i in range(4 if verbosity > 0 else 1)]

    for line in execution.stdout:
        if raw:
            line = line.rstrip()
        else:
            line = line.strip()
        print('>> %s' % line)

    execution.wait()

def cleanup(compiled = True):
    os.remove('%s/%s' % (OUT, SOURCE))
    if compiled:
        os.remove('%s/%s' % (OUT, COMPILED))

if __name__ == '__main__':
    parse_args(sys.argv)

    if len(code_args) == 1 and code_args[0] == '-':
        code_args = read_stdin()

    java_home = find_java_home()
    if not java_home:
        print('| Java home not found, aborting...')
        os.exit(1)

    code = generate_code(' '.join(code_args))
    write_to_file(code, '%s/%s' % (OUT, SOURCE))

    classpath = classpath + find_maven_classpath(mvn)

    if compile(java_home, classpath):
        run(java_home, classpath)
        cleanup()
