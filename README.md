# callswhat
a tool to generate call graphs given an input C source directory

## how to use
there are two modes of operation, one of them tries to get all source files recursively:
```
  ./callswhat.py -d {input_dir} -o {output_file} --cflags {flags}
```
the other is more complicated but is probably more practical for large projects with existing build systems,
you can use pretendcc.py as your compiler and use an existing makefile then it will generate
a temporary file named invkcache.txt which contains the flags for each file, you can then pass that to callswhat.py:
```
*enter directory of a project you'd like a graph for*
./configure CC=/path/to/pretendcc.py
make
./callswhat.py -p invkcache.txt -o graph.dot
```

 ## dependencies:
 
* pygraphviz 	(pip install)
* graphviz 	  (package)
*	llvm 		    (package)
*	clang 		  (package)

![graph](foo.out.png)
