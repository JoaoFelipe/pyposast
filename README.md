PyPosAST
==========

This project extends Python ast nodes with positional informations, such as where the ast node starts and finishes in the code. This allows us to skip using the Python inconsistent lineno and col_offset

I (João Felipe Pimentel) started this library to help me with ast analysis on [noWorkflow](https://github.com/gems-uff/noworkflow)

Installing and using PyPosAST is simple and easy. Please check our installation and basic usage guidelines below.

This package supports Python 2.7, 3.4, 3.5, and 3.6


Quick Installation
------------------

To install PyPosAST, you should follow these basic instructions:

If you have pip, just run:
```bash
$ pip install pyposast
```


If you do not have pip, but already have Git (to clone our repository) and Python:
```bash
$ git clone git@github.com:JoaoFelipe/pyposast.git
$ cd pyposast
$ ./setup.py install
```
This installs PyPosAST on your system.

Usage
-----------

Just use the 'parse' from pyposast it instead of ast.parse:
```python
import pyposast
code = ("variable = 1234\n"
        "if variable:\n"
        "    result = 2 + 2\n"
        "else:\n"
        "    result = 1")
tree = pyposast.parse(code, filename='__main__', mode='exec')
```

This will add the fields first_line, first_col, last_line, last_col, uid, op_pos to the nodes as following:
```
Module -> first_line=1, first_col=0, last_line=5, last_col=14, uid=(5, 14)
  body[0]=Assign: firts_line=1, first_col=0, last_line=1, last_col=15, uid=(1, 15)
    targets[0]=Name: id='variable', first_line=1, firts_col=0, last_line=1, last_col=8, uid=(1, 8)
    op_pos[0]=Node: first_line=1, first_col=9, last_line=1, last_col=10, uid=(1, 10)
    value=Num: n=1234, first_line=1, first_col=11, last_line=1, last_col=15, uid=(1, 15)
  body[1]=If: first_line=2, first_col=0, last_line=5, last_col=14, uid=(2, 2)
    test=Name: id='variable', first_line=2, first_col=3, last_line=2, last_col=11, uid=(2, 11)
    body[0]=Assign: first_line=3, first_col=4, last_line=3, last_col=20, uid=(3, 20)
      targets[0]=Name: id='result', first_line=3, first_col=4, last_line=3, last_col=10, uid=(3, 10)
      op_pos[0]=Node: first_line=3, first_col=11, last_line=3, last_col=12, uid=(3, 12)
      value=BinOp: first_line=3, first_col=13, last_line=3, last_col=18, uid=(3, 18)
        op=Add()
        left=Num: n=2, first_line=3, first_col=13, last_line=3, last_col=14, uid=(3, 14)
        right=Num: n=2, first_line=3, first_col=17, last_line=3, last_col=18, uid=(3, 18)
        op_pos=Node: first_line=3, first_col=15, last_line=3, last_col=16, uid=(3, 16)
    orelse[0]=Assign: first_line=5, first_col=4, last_line=5, last_col=14, uid=(5, 14)
      targets[0]=Name: id='result', first_line=5, first_col=4, last_line=5, last_col=10, uid=(5, 10)
      op_pos[0]=Node: first_line=5, first_col=11, last_line=5, last_col=12, uid=(5, 12)
      value=Num: n=1, first_line=5, first_col=13, last_line=5, last_col=14, uid=(5, 14)
```

The resulting tree can be used as usual with any AST visitor

Contact
----

Do not hesitate to contact me:

* João Felipe Pimentel <joaofelipenp@gmail.com>

License Terms
-------------

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

