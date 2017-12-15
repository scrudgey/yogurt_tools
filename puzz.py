# -*- coding: utf-8 -*-
"""Yogurt commercial puzzle planning code
Using graph theory to plan out the order of puzzles and abilities.
"""

class Node(object):
  def __init__(self, name):
    self.name = name
    self.reqs = []
    self.placed = False
  def req_check(self, nodelist):
    """Check that requirements are met by the nodes in nodelist."""
    # TODO: support ANDs in requirements
    enable = True
    for req in self.reqs:
      if req not in nodelist:
        enable = False
    return enable

class Obstacle(Node):
  def enabled(self, network):
    """given a list of nodes, check that I satisfy my requirements.
    nodelist: list of all currently placed nodes in the tree.
    """
    if placed:
      return False
    nodelist = network.nodes.values()
    return req_check(nodelist)

class Ability(Node):
  def __init__(self, name):
    super().__init__(name)
    self.defeats = []
  def enabled(self, network):
    """check that all precedents have been placed first.
    nodelist: all nodes in my past.
    """
    if placed:
      return False
    nodelist = network.past(self)
    return req_check(nodelist)

  def calc_reqs(self, abilities):
    """Check and see if I obsolete any abilities in the provided list.
    If I do, those abilities must be placed in my immediate past.
    That is checked in enabled() .
    """
    # TODO: implement this
    pass



class Network(object):
  def __init__(self, initial_nodes):
    # TODO: make this a little nicer.
    self.nodes = {}
    self.net = {}
    self.add_obstacle('start')
    for name in initial_nodes:
      self.add_ability(name)
      self.add_connection('start', name)
  def add_obstacle(self, name):
    node = Obstacle(name)
    self.nodes[name] = node
    return node
  def add_ability(self, name):
    node = Ability(name)
    self.nodes[name] = node
    return node

  def defeats(self, ability, obstacle):
    """Ability defeats obstacle."""
    assert ability in self.nodes.keys()
    assert obstacle in self.nodes.keys()
    self.nodes[obstacle].reqs.append(self.nodes[ability])
    self.nodes[ability].defeats.append(self.nodes[obstacle])

  def add_connection(self, node1, node2):
    """node1 is unlocked by node2"""
    if node2 not in self.net.keys():
      self.net[node2] = []
    if node1 not in self.net.keys():
      self.net[node1] = []
    self.net[node1].append(node2)
    self.nodes[node1].placed = True
    self.nodes[node2].placed = True

  def past(self, node):
    """Return the list of all nodes in the past of node"""
    pastnodes = set()
    pastnodes.add(node)
    for req in self.net[node]:
      for newnode in self.past(req):
        pastnodes.add(newnode)
    return pastnodes

  def calc_ability_prereqs(self):
    """Initialize the ability prereqs."""
    for node in self.nodes.values():
      if isinstance(node, Ability):
        node.calc_reqs()

  def enabled_nodes(self, branch):
    """From the branch node, what can I place next?"""
    assert branch in self.net.keys()
    pastnodes = past(self.net[branch])
    enableds = set()
    for node in nodes:
      if node.enabled():
        enableds.add(node)
    return enabled_nodes



# i need a way to differentiate abilities and obstacles
# obstacles have requirements
# both have prereqs but they are calculated different?
