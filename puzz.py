# -*- coding: utf-8 -*-
"""Yogurt commercial puzzle planning code
Using graph theory to plan out the order of puzzles and abilities.
"""

class Node(object):
  def __init__(self, name):
    self.name = name
    self.reqs = set()
    self.placed = False
  def enabled(self, nodelist):
    """Check that requirements are met by the nodes in nodelist."""
    if self.placed:
      return False
    enable = False
    for req in self.reqs:
      if req not in nodelist:
        enable = True
    return enable
class Ability(Node):
  def __init__(self, name):
    super(Ability, self).__init__(name)
    self.defeats = set()
  def enabled(self, nodelist):
    """Check that requirements are met by the nodes in nodelist."""
    if self.placed:
      return False
    enable = True
    for req in self.reqs:
      if req not in nodelist:
        enable = False
    return enable
  def calc_reqs(self, abilities):
    """Check and see if I eclipse any abilities in the provided list.
    If I do, those abilities must be placed in my immediate past.
    That is checked in enabled() .
    """
    for a in abilities:
      if a == self:
        continue
      # i eclipse an ability if, for every obstacle it can
      # defeat, i can defeat it too
      eclipsed = True
      for d in a.defeats:
        if d not in self.defeats:
          eclipsed = False
      if eclipsed:
        self.reqs.add(a.name)


class Network(object):
  def __init__(self, initial_nodes):
    self.nodes = {}
    self.abilities = {}
    self.obstacles = {}
    self.net = {}
    self.add_obstacle('start')
    self.net['start'] = []
    # TODO: make this a little nicer?
    for name in initial_nodes:
      self.add_ability(name)
      self.add_connection('start', name)
  def add_obstacle(self, name):
    """Create a new obstacle node."""
    node = Node(name)
    self.nodes[name] = node
    self.obstacles[name] = node
  def add_ability(self, name):
    """Create a new ability node."""
    node = Ability(name)
    self.nodes[name] = node
    self.abilities[name] = node
  def past(self, node):
    """Return a list of all nodes that had to have been
    visited by the player before node.
    """
    assert node in self.net
    pastnodes = set()
    pastnodes.add(node)
    for req in self.net[node]:
      for newnode in self.past(req):
        pastnodes.add(newnode)
    return pastnodes
  def calc_ability_prereqs(self):
    """Initialize the ability prereqs."""
    for a in self.abilities.values():
      a.calc_reqs(self.abilities.values())

  def defeats(self, ability, obstacle):
    """Ability defeats obstacle."""
    assert ability in self.abilities
    assert obstacle in self.obstacles
    self.obstacles[obstacle].reqs.add(ability)
    self.abilities[ability].defeats.add(obstacle)
  def add_connection(self, node1, node2):
    """node1 unlocks node2"""
    assert node1 in self.net
    assert node2 in self.nodes
    assert node2 in self.enabled_nodes(node1)
    if node2 not in self.net:
      self.net[node2] = []
    self.net[node2].append(node1)
    self.nodes[node1].placed = True
    self.nodes[node2].placed = True

  def enabled_nodes(self, branch):
    """From the branch node, what can I place next?"""
    assert branch in self.net
    placed_nodes = [n.name for n in self.nodes.values() if n.placed]
    enableds = set()
    for obstacle in self.obstacles.values():
      if obstacle.enabled(placed_nodes):
        enableds.add(obstacle.name)
    for ability in self.abilities.values():
      if ability.enabled(self.past(branch)):
        enableds.add(ability.name)
    return enableds



# i need a way to differentiate abilities and obstacles
# obstacles have requirements
# both have prereqs but they are calculated different?
