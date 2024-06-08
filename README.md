PyPosAST
==========

This project extends Python ast nodes with positional informations, such as where the ast node starts and finishes in the code.

I (João Felipe Pimentel) started this library to help me with ast analysis to help me with ast analises on [noWorkflow](https://github.com/gems-uff/noworkflow).

Installing and using PyPosAST is simple and easy. Please check our installation and basic usage guidelines below.

This package currently supports Python 2.7, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13.0b2


Differences between Python AST positions and PyPosAST positions.
------------------


This project was originally created before Python 3.9 added `end_lineno` and `end_col_offset` with the goal of fully identifying the AST nodes in the code. Thus, it enrinches the existing AST nodes with different attributes:

<table>
<tr>
<th>Attribute</th>
<th>AST</th>
<th>PyPosAST</th>
</tr>
<tr>
<th>Start line</th>
<td>

`node.lineno`

</td>
<td>

`node.first_line`

</td>
</tr>
<tr>
<th>Start column</th>
<td>

`node.col_offset`

</td>
<td>

`node.first_col`

</td>
</tr>
<tr>
<th>End line</th>
<td>

`node.end_lineno`

</td>
<td>

`node.last_line`

</td>
</tr>
<tr>
<th>End column</th>
<td>

`node.end_lineno`

</td>
<td>

`node.last_col`

</td>
</tr>

</table>



There are also some key differences on the interpretation of what is the start and the end of a node.

- In function definitions and class definitions that have decorators, PyPosAST considers the start of the FunctionDef node as the start of the first decorator, while Python AST uses the start of `def`/`class`.
- In expressions surrounded by parentheses, PyPosAST includes the parentheses in the position of the node.
- In match_case nodes, PyPosAST includes the case keyword as part of the node to be consistent with other types of nodes.

Moreover, PyPosAST extracts some positions that the Python AST does not extract (e.g., positions of identifier nodes, which are str on the ast). Some of them are available on pseudo-nodes (`node.name_node`, `node.op_pos`, ...), while other positions are integrated on the nodes themselves.

The following table presents some of these differences.

<table>
<tr>
<th> Code </th>
<th> Node </th>
<th> Tool </th>
<th> Start line </th>
<th> Start column </th>
<th> End line </th>
<th> End column </th>
</tr>
<tr>
<td rowspan="3">

```python
@dec
def f():
    pass
```

</td>
<td rowspan="2">FunctionDef</td>
<td>AST</td>
<td style="color: blue">2</td>
<td>0</td>
<td>3</td>
<td>7</td>
</tr>
<tr>
<td>PyPosAST</td>
<td style="color: blue">1</td>
<td>0</td>
<td>3</td>
<td>7</td>
</tr>
<tr>
<td style="color: blue">FunctionDef.name_node</td>
<td>PyPosAST</td>
<td>2</td>
<td>4</td>
<td>2</td>
<td>5</td>
</tr>

<tr>
<td rowspan="2">

```python
(a.b)
```

</td>
<td rowspan="2">Attribute</td>
<td>AST</td>
<td>1</td>
<td style="color: blue">1</td>
<td>1</td>
<td style="color: blue">4</td>
</tr>
<tr>
<td>PyPosAST</td>
<td>1</td>
<td style="color: blue">0</td>
<td>1</td>
<td style="color: blue">5</td>
</tr>

<tr>
<td rowspan="2">

```python
match x:
    case y:
        pass
```

</td>
<td rowspan="2">match_case</td>
<td>AST</td>
<td>2</td>
<td style="color: blue">9</td>
<td style="color: blue">-</td>
<td style="color: blue">-</td>
</tr>
<tr>
<td>PyPosAST</td>
<td>2</td>
<td style="color: blue">4</td>
<td style="color: blue">3</td>
<td style="color: blue">12</td>
</tr>


</table>


Limitation: PyPosAST currently only works with unicode code, since it parses the script again to obtain the position of all elements.



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

