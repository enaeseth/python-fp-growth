# encoding: utf-8

"""
A Python implementation of the FP-growth algorithm.
"""

__author__ = 'Eric Naeseth <enaeseth@gmail.com>'
__copyright__ = 'Copyright © 2009 Eric Naeseth'
__license__ = 'MIT License'

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
        self._paths = {}
        
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
                
                # Update the path of nodes that contain this item to include
                # our new node.
                try:
                    path = self._paths[item]
                    path[1].neighbor = next_point # path[1] is the tail
                    path[1] = next_point
                except KeyError:
                    # First node for this item; start a new path.
                    self._paths[item] = [next_point, next_point]
                    
            point = next_point
        
    
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
        
    def parent():
        doc = "The node's parent."
        def fget(self):
            return self._parent
        def fset(self, value):
            if not isinstance(value, FPNode):
                raise TypeError("A node must have an FPNode as a parent.")
            if value.tree is not self.tree:
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
            if not isinstance(value, FPNode):
                raise TypeError("A node must have an FPNode as a neighbor.")
            if value.tree is not self.tree:
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

