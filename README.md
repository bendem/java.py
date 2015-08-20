## java.py

`java.py` is a python script allowing you to execute java code quickly without opening an IDE
or typing all the boilerplate code:

```
$ java.py 'Stream.of(1, 2, 3, 4).map(Integer::toBinaryString)'
>> ['1', '10', '11', '100']
```

The result of the last instruction is displayed:
```
$ java.py 'Scanner s = new Scanner(System.in); s.nextLine()'
hello world!
 >> hello world!
```

The collection/array formatting allows you to quickly identify contained types:
```
$ java.py "new Object[]{1, \"a\", null, 'a'}"
 >> [1, "a", null, 'a']

 $ java.py 'Set<String> s = new HashSet<>(); s.add("hello"); s.add("world!"); s'
 >> ["hello", "world!"]
```

Missing an import? You can add content at the start of the generated file with `-s`:
```
$ java.py -s 'import java.time.*' 'Instant.now()'
 >> 2015-08-20T20:16:58.753Z
```

Want a pretty output? Use the `-p` flag:
```
$ java.py -p 'Random r = new Random(); Stream.generate(r::nextInt).limit(5)'
 >> [-464730534,
 >> -488917297,
 >> -846999467,
 >> 5521057,
 >> -366992486]
```

### Requirements

Requires java 8 and python 3 to work.
