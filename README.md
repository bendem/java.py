## java.py

`java.py` is a python script allowing you to execute java code quickly without opening an IDE
or typing all the boilerplate code:

```
$ java.py 'Stream.of(1, 2, 3, 4).map(Integer::toBinaryString)'
 >> (java.util.stream.ReferencePipeline$3) ["1", "10", "11", "100"]
```

The result of the last instruction is displayed:
```
$ java.py 'Scanner s = new Scanner(System.in); s.nextLine()' <<< 'hello world!'
 >> (String) hello world!
```

The collection/array formatting allows you to quickly identify contained types:
```
$ java.py "Object[] a = new Object[]{1, \"a\", null, 'a'}; a"
 >> (Object[]) [1, "a", null, 'a']

 $ java.py 'Set<String> s = new HashSet<>(); s.add("hello"); s.add("world!"); s'
 >> (java.util.HashSet) ["hello", "world!"]
```

Missing an import? You can add content at the start of the generated file with `-s`:
```
$ java.py -s 'import java.time.*' 'Instant.now()'
 >> (java.time.Instant) 2016-02-29T12:44:54.870Z
```

Want a pretty output? Use the `-p` flag:
```
$ java.py -p 'Random r = new Random(); Stream.generate(r::nextInt).limit(5)'
 >> (java.util.stream.SliceOps$1) [1716066362,
 >> 403370638,
 >> 653951165,
 >> -2063181131,
 >> -862370509]
```

### Requirements

Requires java 8 and python 3 to work.
