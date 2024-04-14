# An ADAPT implementation of the Insertion Search Tree data structure.
# Based on a Red-Black Tree, modified for file insertion history tracking.

class IST:
    def __init__(self, skeleton):
        self.skeleton = skeleton
        self.data = skeleton
        self.tree = ISTree()

    def replace(self, pos, size, text):
        real_pos = self.pos(pos)
        self.data = self.data[:real_pos] + text + self.data[real_pos + size:]
        self.tree.insert(pos, len(text) - size)
    
    def insert(self, pos, text):
        self.replace(pos, 0, text)
    
    def pos(self, key):
        shift = self.tree.get(key)
        return key + shift
    
    def line_pos(self, pos):
        real_pos = self.pos(pos)
        return self.data.count('\n', 0, real_pos)

    def get_skeleton(self):
        return self.skeleton
    
    def view(self):
        return self.data


class Node:
    def __init__(self, key, shift, color="red", parent=None, left=None, right=None):
        self.key = key
        self.shift = shift
        self.accumulated_shift = shift
        self.color = color
        self.parent = parent
        self.left = left
        self.right = right


class ISTree:
    def __init__(self):
        self.NIL = Node(None, None, "black")
        self.root = self.NIL

    def insert(self, key, shift):
        """Insert a key and its shift into the tree."""
        new_node = Node(key, shift, parent=self.NIL, left=self.NIL, right=self.NIL)
        self._insert(new_node)
        self._fix_insert(new_node)

    def _insert(self, node):
        """Insert a node into the tree, ignoring color."""
        y = self.NIL
        x = self.root
        while x is not self.NIL:
            y = x
            if node.key < x.key:
                x.accumulated_shift += node.shift
                x = x.left
            else:
                x = x.right
        node.parent = y
        if y is self.NIL:
            self.root = node
        elif node.key < y.key:
            y.left = node
        else:
            y.right = node
        node.left = self.NIL
        node.right = self.NIL
        #print_tree(ist.root)

    def _fix_insert(self, k):
        while k.parent.color == "red":
            if k.parent == k.parent.parent.right:
                u = k.parent.parent.left  # uncle
                if u.color == "red":
                    u.color = "black"
                    k.parent.color = "black"
                    k.parent.parent.color = "red"
                    k = k.parent.parent
                else:
                    if k == k.parent.left:
                        k = k.parent
                        self._rotate_right(k)
                    k.parent.color = "black"
                    k.parent.parent.color = "red"
                    self._rotate_left(k.parent.parent)
            else:
                u = k.parent.parent.right  # uncle
                if u.color == "red":
                    u.color = "black"
                    k.parent.color = "black"
                    k.parent.parent.color = "red"
                    k = k.parent.parent
                else:
                    if k == k.parent.right:
                        k = k.parent
                        self._rotate_left(k)
                    k.parent.color = "black"
                    k.parent.parent.color = "red"
                    self._rotate_right(k.parent.parent)
        self.root.color = "black"

    def _rotate_left(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent == self.NIL:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y
        y.accumulated_shift += x.accumulated_shift

    def _rotate_right(self, x):
        y = x.left
        x.left = y.right
        if y.right != self.NIL:
            y.right.parent = x
        y.parent = x.parent
        if x.parent == self.NIL:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y
        x.accumulated_shift -= y.accumulated_shift

    def get(self, key):
        """Return the accumulated shift for the given key."""
        node = self.root
        accumulated_shift = 0
        while node != self.NIL:
            if key < node.key:
                node = node.left
            else:
                accumulated_shift += node.accumulated_shift
                if key == node.key:
                    return accumulated_shift
                node = node.right
        return accumulated_shift  # if the key not found, return the shift of the nearest lower key
    

def _print_tree(node, level=0):
    if node is not None:
        _print_tree(node.right, level + 1)
        print(' ' * 4 * level + ('R-' if node.color == "red" else 'B-') + str(node.key) + 
              (':' + str(node.shift) + (':' + str(node.accumulated_shift)) if node.accumulated_shift is not None else ''))
        _print_tree(node.left, level + 1)

def print_tree(node):
    print('-------- Tree -------')
    _print_tree(node)
    print('---------------------')

ist = ISTree()
# print_tree(ist.root)
# ist.insert(1, 10)
# print_tree(ist.root)
# ist.insert(2, 20)
# print_tree(ist.root)
# ist.insert(3, 30)
# print_tree(ist.root)
# print(ist.get(1))  # Should print 10
# print_tree(ist.root)
# print(ist.get(2))  # Should print 30
# print_tree(ist.root)
# print(ist.get(3))  # Should print 60
# print_tree(ist.root)
# print(ist.get(4))  # Should print None
# print_tree(ist.root)
# for i in range(4, 100):
#     ist.insert(i, i * 10)
#     print(ist.get(i))  # Should print sum of 10 * j for j in range(1, i+1)
#     print_tree(ist.root)

# ist = ISTree()
# ist.insert(23, 20)
# ist.insert(98, 5)
# print_tree(ist.root)
# ist.insert(70, 4)
# print_tree(ist.root)
# ist.insert(61, 10)
# print_tree(ist.root)
# ist.insert(64, 3)
# print_tree(ist.root)
# ist.insert(5, 13)
# print_tree(ist.root)
# ist.insert(78, 2)
# print_tree(ist.root)
# ist.insert(89, 30)
# print_tree(ist.root)
# print(ist.get(98))

# ist = ISTree()
# insertions = [
#     (70, 4),
#     (89, 30),
#     (64, 3),
#     (98, 5),
#     (23, 20),
#     (78, 2),
#     (5, 13),
#     (61, 10)
# ]
# # shuffle the insertions
# import random
# random.shuffle(insertions)

# for line, shift in insertions:
#     ist.insert(line, shift)
#     print_tree(ist.root)

# print(ist.get(98))

# for i in range(10):
#     ist = ISTree()
#     random.shuffle(insertions)
#     for line, shift in insertions:
#         ist.insert(line, shift)
#     print(ist.get(98))


##############   Testing insertion order insensitivity  #############
import random
def CreateTree( insertions ):
    ist = ISTree()
    for pos, shift in insertions:
        ist.insert(pos, shift)
    return ist

def Test( N: int = 1000, Iterations: int = 10000 ):
    Iterations = 100 if Iterations < 100 else Iterations
    insertions = [(i, random.randint(0, 100 * N)) for i in range(N)]
    ist = CreateTree(insertions)

    # pick a random pos number from the insertions list
    pos = random.choice(insertions)[0]
    shift = ist.get(pos)

    for i in range(Iterations):
        # print progress every 5% percent of all iteration number
        if i % (Iterations // (100 / 5)) == 0:
            print(f'{(i / Iterations) * 100:.2f}% passed')
        
        random.shuffle(insertions)
        ist = CreateTree(insertions)
        assert(ist.get(pos) == shift)
        #print(f'Pos: {pos}, Shift: {shift}, Iterations: {i}')
    print('Test Passed')

if __name__ == '__main__':
    Test()


# And sir dare view but over man.
# So at within mr to simple assure.
# Mr disposing continued it offending arranging in we.
# Extremity as if breakfast agreement.
# <!-- EXAMPLE -->
# Off now mistress provided out horrible opinions.
# Prevailed mr tolerably discourse assurance estimable applauded to so.
# Him everything melancholy uncommonly but solicitude inhabiting projection off.
# Connection stimulated estimating excellence an to impression.

# Attended no do thoughts me on dissuade scarcely.
# Own are pretty spring suffer old denote his.
# By proposal speedily mr striking am.
# But attention sex questions applauded how happiness.
# To travelling occasional at oh sympathize prosperous.
# His merit end means widow songs linen known.
# Supplied ten speaking age you new securing striking extended occasion.
# Sang put paid away joy into six her.

# Old unsatiable our now but considered travelling impression.
# In excuse hardly summer in basket misery.
# By rent an part need.
# <!-- EXAMPLE -->
# At wrong of of water those linen.
# Needed oppose seemed how all.
# Very mrs shed shew gave you.
# Oh shutters do removing reserved wandered an.
# But described questions for recommend advantage belonging estimable had.
# Pianoforte reasonable as so am inhabiting.
# Chatty design remark and his abroad figure but its.

# Started earnest brother believe an exposed so.
# Me he believing daughters if forfeited at furniture.
# Age again and stuff downs spoke.
# <!-- EXAMPLE -->
# Late hour new nay able fat each sell.
# Nor themselves age introduced frequently use unsatiable devonshire get.
# They why quit gay cold rose deal park.
# One same they four did ask busy.
# Reserved opinions fat him nay position.
# Breakfast as zealously incommode do agreeable furniture.
# One too nay led fanny allow plate.

# <!-- EXAMPLE -->
# Too cultivated use solicitude frequently.
# Dashwood likewise up consider continue entrance ladyship oh.
# Wrong guest given purse power is no.
# Friendship to connection an am considered difficulty.
# Country met pursuit lasting moments why calling certain the.
# Middletons boisterous our way understood law.
# Among state cease how and sight since shall.
# Material did pleasure breeding our humanity she contempt had.
# So ye really mutual no cousin piqued summer result.

# <!-- EXAMPLE -->
# Mr do raising article general norland my hastily.
# Its companions say uncommonly pianoforte favourable.
# Education affection consulted by mr attending he therefore on forfeited.
# High way more far feet kind evil play led.
# Sometimes furnished collected add for resources attention.
# <!-- EXAMPLE -->
# Norland an by minuter enquire it general on towards forming.
# Adapted mrs totally company two yet conduct men.
# <!-- EXAMPLE -->

# Insipidity the sufficient discretion imprudence resolution sir him decisively.
# Proceed how any engaged visitor.
# Explained propriety off out perpetual his you.
# Feel sold off felt nay rose met you.
# <!-- EXAMPLE -->
# We so entreaties cultivated astonished is.
# Was sister for few longer mrs sudden talent become.
# Done may bore quit evil old mile.
# If likely am of beauty tastes.

# Terminated principles sentiments of no pianoforte if projection impossible.
# Horses pulled nature favour number yet highly his has old.
# <!-- EXAMPLE -->
# Contrasted literature excellence he admiration impression insipidity so.
# Scale ought who terms after own quick since.
# Servants margaret husbands to screened in throwing.
# Imprudence oh an collecting partiality.
# Admiration gay difficulty unaffected how.

# Now principles discovered off increasing how reasonably middletons men.
# Add seems out man met plate court sense.
# His joy she worth truth given.
# All year feet led view went sake.
# <!-- EXAMPLE -->
# You agreeable breakfast his set perceived immediate.
# Stimulated man are projecting favourable middletons can cultivated.

# In entirely be to at settling felicity.
# Fruit two match men you seven share.
# Needed as or is enough points.
# Miles at smart ﻿no marry whole linen mr.
# Income joy nor can wisdom summer.
# <!-- EXAMPLE -->
# Extremely depending he gentleman improving intention rapturous as.
