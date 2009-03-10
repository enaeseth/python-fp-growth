# encoding: utf-8

"""
A Python implementation of the FP-growth algorithm.
"""

from collections import defaultdict
from itertools import imap

__author__ = 'Eric Naeseth <enaeseth@gmail.com>'
__copyright__ = 'Copyright © 2009 Eric Naeseth'
__license__ = 'MIT License'

def find_frequent_itemsets(transactions, minimum_support):
    """
    Finds frequent itemsets in the given transactions using FP-growth. This
    function returns a generator instead of an eagerly-populated list of items.
    
    The `transactions` parameter can be any iterable of iterables of items.
    `minimum_support` should be an integer specifying the minimum number of
    occurrences of an itemset for it to be accepted.
    """
    items = defaultdict(lambda: 0) # mapping from items to their supports
    processed_transactions = []
    
    # Load the passed-in transactions and count the support that individual
    # items have.
    for transaction in transactions:
        processed = []
        for item in transaction:
            items[item] += 1
            processed.append(item)
        processed_transactions.append(processed)
    
    # Remove infrequent items from the item support dictionary.
    items = dict(items)
    for item, support in items.iteritems():
        if support < minimum_support:
            del items[item]
    
    # Build our FP-tree. Before any transactions can be added to the tree, they
    # must be stripped of infrequent items and their surviving items must be
    # sorted in decreasing order of frequency.
    def clean_transaction(transaction):
        transaction = filter(lambda v: v in items, transaction)
        transaction.sort(key=lambda v: items[v], reverse=True)
        return transaction
        
    master = FPTree()
    for transaction in imap(clean_transaction, processed_transactions):
        master.add(transaction)
    
    def find_with_suffix(tree, suffix):
        for item, nodes in tree.items():
            support = sum(n.count for n in nodes)
            if support >= minimum_support:
                # New winner!
                found_set = [item] + suffix
                yield found_set
                
                # Build a conditional tree and recursively search for frequent
                # itemsets within it.
                cond_tree = conditional_tree_from_paths(tree.prefix_paths(item),
                    minimum_support)
                for s in find_with_suffix(cond_tree, found_set):
                    yield s # pass along the good news to our caller
    
    # Search for frequent itemsets, and yield the results we find.
    for s in find_with_suffix(master, []):
        yield s

class FPTree(object):
    """
    An FP tree.
    
    This object may only store transaction items that are hashable (i.e., all
    items must be valid as dictionary keys or set members).
    """
    def __init__(self):
        # The root node of the tree.
        self._root = FPNode(self, None, None)
        
        # A dictionary mapping items to the head and tail of a path of
        # "neighbors" that will hit every node containing that item.
        self._routes = {}
        
    @property
    def root(self):
        """The root node of the tree."""
        return self._root
        
    def add(self, transaction):
        """
        Adds a transaction to the tree.
        """
        
        point = self._root
        
        for item in transaction:
            next_point = point.search(item)
            if next_point:
                # There is already a node in this tree for the current
                # transaction item; reuse it.
                next_point.increment()
            else:
                # Create a new point and add it as a child of the point we're
                # currently looking at.
                next_point = FPNode(self, item)
                point.add(next_point)
                
                # Update the route of nodes that contain this item to include
                # our new node.
                self._update_route(next_point)
                    
            point = next_point
            
    def _update_route(self, point):
        assert self is point.tree
        
        try:
            route = self._routes[point.item]
            route[1].neighbor = point # route[1] is the tail
            route[1] = point
        except KeyError:
            # First node for this item; start a new route.
            self._routes[point.item] = [point, point]
            
    def items(self):
        """
        Generate one 2-tuples for each item represented in the tree. The first
        element of the tuple is the item itself, and the second element is a
        generator that will yield the nodes in the tree that belong to the item.
        """
        for item in self._routes.iterkeys():
            yield (item, self.nodes(item))
    
    def nodes(self, item):
        """
        Generates the sequence of nodes that contain the given item.
        """
        
        try:
            node = self._routes[item][0]
        except KeyError:
            return
            
        while node:
            yield node
            node = node.neighbor
    
    def prefix_paths(self, item):
        """Generates the prefix paths that end with the given item."""
        
        def collect_path(node):
            path = []
            while node and not node.root:
                path.append(node)
                node = node.parent
            path.reverse()
            return path
            
        return (collect_path(node) for node in self.nodes(item) if node.leaf)
        
    def _removed(self, node):
        """Called when `node` is removed from the tree; performs cleanup."""
        
        head, tail = self._routes[node.item]
        if node is head:
            if node is tail or not node.neighbor:
                # It was the sole node.
                del self._routes[node.item]
            else:
                self._routes[node.item][0] = node.neighbor
        else:
            for n in self.nodes(node.item):
                if n.neighbor is node:
                    n.neighbor = node.neighbor # skip over
                    if node is tail:
                        self._routes[node.item][1] = n
                    break

def conditional_tree_from_paths(paths, minimum_support):
    """Builds a conditional FP-tree from the given prefix paths."""
    tree = FPTree()
    condition_item = None
    items = set()
    
    # Import the nodes in the paths into the new tree. Only the counts of the
    # leaf notes matter; the remaining counts will be reconstructed from the
    # leaf counts.
    for path in paths:
        if condition_item is None:
            condition_item = path[-1]
        
        point = tree.root
        for node in path:
            next_point = point.search(node.item)
            if not next_point:
                items.add(node.item)
                count = node.count if node.leaf else 0
                next_point = FPNode(tree, node.item, count)
                point.add(next_point)
                tree._update_route(next_point)
            point = next_point
    
    assert condition_item is not None
                
    # Calculate the counts of the non-leaf nodes.
    for path in tree.prefix_paths(condition_item):
        count = None
        for node in reversed(path):
            if count is not None:
                node._count += count
            count = node.count
    
    # Eliminate the nodes for any items that are no longer frequent.
    for item in items:
        support = sum(n.count for n in tree.nodes(item))
        if support < minimum_support:
            # Doesn't make the cut anymore
            for node in tree.nodes(item):
                node.parent.remove(node)
                
    # Finally, remove the nodes corresponding to the item for which this
    # conditional tree was generated.
    for node in tree.nodes(condition_item):
        node.parent.remove(item)
        
    return tree
    
class FPNode(object):
    """A node in an FP tree."""
    
    def __init__(self, tree, item, count=1):
        self._tree = tree
        self._item = item
        self._count = count
        self._parent = None
        self._children = {}
        self._neighbor = None
        
    def add(self, child):
        """Adds the given FPNode `child` as a child of this node."""
        
        if not isinstance(child, FPNode):
            raise TypeError("Can only add other FPNodes as children")
        
        if not child.item in self._children:
            self._children[child.item] = child
            child.parent = self
        
    def search(self, item):
        """
        Checks to see if this node contains a child node for the given item.
        If so, that node is returned; otherwise, `None` is returned.
        """
        
        try:
            return self._children[item]
        except KeyError:
            return None
            
    def remove(self, child):
        try:
            if self._children[child.item] is child:
                del self._children[child.item]
                child.parent = None
                self._tree._removed(child)
            else:
                raise ValueError("that node is not a child of this node")
        except KeyError:
            raise ValueError("that node is not a child of this node")
            
    def __contains__(self, item):
        return item in self._children
        
    @property
    def tree(self):
        """The tree in which this node appears."""
        return self._tree
    
    @property
    def item(self):
        """The item contained in this node."""
        return self._item
    
    @property
    def count(self):
        """The count associated with this node's item."""
        return self._count
        
    def increment(self):
        """Increments the count associated with this node's item."""
        if self._count is None:
            raise ValueError("Root nodes have no associated count.")
        self._count += 1
        
    @property
    def root(self):
        """True if this node is the root of a tree; false if otherwise."""
        return self._item is None and self._count is None
        
    @property
    def leaf(self):
        """True if this node is a leaf in the tree; false if otherwise."""
        return len(self._children) == 0
        
    def parent():
        doc = "The node's parent."
        def fget(self):
            return self._parent
        def fset(self, value):
            if value is not None and not isinstance(value, FPNode):
                raise TypeError("A node must have an FPNode as a parent.")
            if value and value.tree is not self.tree:
                raise ValueError("Cannot have a parent from another tree.")
            self._parent = value
        return locals()
    parent = property(**parent())
    
    def neighbor():
        doc = """
        The node's neighbor; the one with the same value that is "to the right"
        of it in the tree.
        """
        def fget(self):
            return self._neighbor
        def fset(self, value):
            if value is not None and not isinstance(value, FPNode):
                raise TypeError("A node must have an FPNode as a neighbor.")
            if value and value.tree is not self.tree:
                raise ValueError("Cannot have a neighbor from another tree.")
            self._neighbor = value
        return locals()
    neighbor = property(**neighbor())
    
    @property
    def children(self):
        """The nodes that are children of this node."""
        return tuple(self._children.itervalues())
    
    
    def __repr__(self):
        if self.root:
            return "<%s (root)>" % type(self).__name__
        return "<%s %r (%r)>" % (type(self).__name__, self.item, self.count)

