Python FP-Growth
================

This module provides a pure Python implementation of the FP-growth algorithm for
finding frequent itemsets. FP-growth exploits an (often-valid) assumption that
many transactions will have items in common to build a prefix tree. If the
assumption holds true, this tree produces a compact representation of the actual
transactions and is used to generate itemsets much faster than *Apriori* can.

Installation
------------

After downloading and extracting the package, install the module by running
`python setup.py install` from within the extracted package directory. (If you
encounter errors, you may need to run setup with elevated permissions:
`sudo python setup.py install`.)

Library Usage
-------------

Usage of the module is very simple. Assuming you have some iterable of transactions (which are themselves iterables of items) called `transactions` and
an integer minimum support value `minsup`, you can find the frequent itemsets
in your transactions with the following code:

    from fp_growth import find_frequent_itemsets
    for itemset in find_frequent_itemsets(transactions, minsup):
        print itemset
        
Note that `find_frequent_itemsets` returns a generator of itemsets, not a
greedily-populated list. Each item must be hashable (i.e., it must be valid as
a member of a dictionary or a set).

Script Usage
------------

Once installed, the module can also be used as a stand-alone script. It will
read a list of transactions formatted as a CSV file. (An example of such a file
in included in the `examples` directory.)

    python -m fp_growth -s {minimum support} {path to CSV file}
    
For example, to find the itemsets with support ≥ 4 in the included example file:

    python -m fp_growth -s 4 examples/tsk.csv

References
----------

The following references were used as source descriptions of the algorithm:

- Tan, Pang-Ning, Michael Steinbach, and Vipin Kumar. Introduction to Data
  Mining. 1st ed. Boston: Pearson / Addison Wesley, 2006. (pp. 363-370) 
- Han,  Jiawei, Jian Pei, and Yiwen Yin. "Mining Frequent Patterns without
  Candidate Generation." Proceedings of the 2000 ACM SIGMOD international
  conference on Management of data, 2000.
  
The example data included in `tsk.csv` comes from the section in *Introduction
to Data Mining*.

License
-------

The `python-fp-growth` package is made available under the terms of the
MIT License.

Copyright © 2009 [Eric Naeseth][me]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

[me]: http://github.com/enaeseth/
[pypi]: http://pypi.python.org/