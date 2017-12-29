# -*- coding: utf-8 -*-
"""Yogurt commercial puzzle planning code
Using graph theory to plan out the order of puzzles and abilities.
"""
import networkx as nx
import itertools
import collections
import copy
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

class Node(object):
  def __init__(self, name):
    self.name = name
    self.reqs = set()
    self.placed = False
  def all_in(self, rlist, nodelist):
    """Are all items in rlist are in nodelist?"""
    ins = [r in nodelist for r in rlist]
    return all(ins)
  def enabled(self, nodelist):
    """Check that requirements are met by the nodes in nodelist."""
    enable = False
    for req in self.reqs:
      if isinstance(req, tuple):
        enable = enable or self.all_in(req, nodelist)
      else:
        enable = enable or req in nodelist
    return enable
  def enablers(self, nodelist):
    """Which nodes in nodelist enab
    """
    required = set()
    for req in self.reqs:
      if isinstance(req, tuple):
        if self.all_in(req, nodelist):
          required.add(req)
      else:
        if req in nodelist:
          required.add(req)
    return required


class Ability(Node):
  def __init__(self, name):
    super(Ability, self).__init__(name)
    self.defeats = set()
  def enabled(self, nodelist):
    """Check that requirements are met by the nodes in nodelist."""
    if len(self.reqs) > 0:
      return self.all_in(self.reqs, nodelist)
    else:
      return True
  def calc_eclipses(self, abilities):
    """Check and see if I eclipse any abilities in the provided list.
    If I do, those abilities must be placed in my immediate past.
    That is checked in enabled() .
    """
    for a in abilities:
      if a == self:
        continue
      # i eclipse an ability if, for every obstacle it can
      # defeat, i can defeat it too
      overlaps = [d in self.defeats for d in a.defeats]
      if len(overlaps) == 0:
        continue
      if all(overlaps) and len(self.defeats) != len(a.defeats):
        self.reqs.add(a.name)

class Network(object):
  def __init__(self, initial_nodes):
    self.nodes = {}
    self.abilities = {}
    self.obstacles = {}
    self.net = {}
    self.add_obstacle('start')
    self.net['start'] = set()
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
  def calc_ability_eclipses(self):
    """Initialize the ability eclipses."""
    for a in self.abilities.values():
      a.reqs = set()
      a.calc_eclipses(self.abilities.values())
  def defeats(self, ability, obstacle):
    """Ability defeats obstacle."""
    assert obstacle in self.obstacles
    ob = self.obstacles[obstacle]
    if isinstance(ability, tuple):
      for a in ability:
        assert a in self.abilities
    else:
      assert ability in self.abilities
      self.abilities[ability].defeats.add(obstacle)
    ob.reqs.add(ability)
    self.calc_ability_eclipses()
  def add_connection(self, node1, node2):
    """node1 unlocks node2"""
    assert node1 in self.net
    assert node2 in self.nodes
    enabled = self.enabled_nodes(node1)
    assert node2 in enabled or node2 in self.net
    if node2 not in self.net:
      self.net[node2] = set()
    self.nodes[node1].placed = True
    self.nodes[node2].placed = True
    multis = [isinstance(req, tuple) for req in enabled[node2]]
    if all(multis) and len(multis) > 0:
      for req in enabled[node2]:
        for r in req:
          self.net[node2].add(r)
    else:
      self.net[node2].add(node1)

  def enabled_nodes(self, branch, suppress_live=False):
    """From the branch node, what can I place next?"""
    assert branch in self.net
    placed_nodes = self.net.keys()
    enableds = {}
    for obstacle in self.obstacles.values():
      if obstacle.enabled(placed_nodes):
        enableds[obstacle.name] = obstacle.enablers(placed_nodes)
    # if branch in self.obstacles:
    for ability in self.abilities.values():
      pastbranch = self.past(branch)
      if ability.enabled(pastbranch):
        enableds[ability.name] = ability.enablers(pastbranch)
    if suppress_live:
      placed_nodes = [node for node in enableds if self.nodes[node].placed]
      for node in placed_nodes:
        enableds.pop(node, None)
    return enableds
  def locked_abilities(self):
    """Return a list of all abilities that are still
    eclipsed.
    Recall that all of the requirements of a given ability
    must be in its immediate past.
    """
    eclipsed = {}
    # a dictionary like node: requirements
    for a in self.abilities.keys():
      eclipsed[a] = set(self.nodes[a].reqs)
    # remove all enabled nodes
    for node in self.net:
      for enabled in self.enabled_nodes(node):
        eclipsed.pop(enabled, None)
    for a in eclipsed.keys():
      for node in self.net:
        past = self.past(node)
        reqs_met = [req in past for req in self.nodes[a].reqs]
        if all(reqs_met):
          eclipsed.pop(a, None)
    return eclipsed
  def locked_obstacles(self, potential=True):
    """Return a list of all obstacles that are still locked.
    These are potential obstacles to look at placing.
    By default, it will only show those that don't require
    locked abilities. (potential=True)
    """
    locked = {}
    for o in self.obstacles.keys():
      locked[o] = set(self.nodes[o].reqs)
    for enabled in self.enabled_nodes('start'):
      locked.pop(enabled, None)
    # TODO: if something only requires an eclipsed ability,
    # then it is unlocked for the net in general if not start specifically
    for enabled in self.net:
      for l in locked:
        locked[l].discard(enabled)
    if potential:
      eclipsed = self.locked_abilities()
      unreasonable = set()
      for l in locked:
        requires_locked = [req in eclipsed for req in locked[l]]
        if all(requires_locked) and len(requires_locked) > 0:
          unreasonable.add(l)
      for l in unreasonable:
        locked.pop(l, None)
    return locked
  def compare(self, ability1, ability2):
    """Show the overlap and non-overlap between the
    obstacles that are defeated by two abilities.
    """
    d1 = self.nodes[ability1].defeats
    d2 = self.nodes[ability2].defeats
    overlap = d1.intersection(d2)
    nonoverlap = d1.union(d2) - overlap
    print 'overlap:'
    print overlap
    print 'non overlap:'
    print nonoverlap
  def active_abilities(self):
    """Print all the active abilities in the net"""
    print [node for node in net.abilities if net.abilities[node].placed]
  def active_obstacles(self):
    """Print all the active obstacles in the net"""
    print [node for node in net.obstacles if net.obstacles[node].placed]
  def unlocked_obstacles(self):
    """Print all of the obstacles that can be placed."""
    unlocked = set()
    for node in self.net:
      for enabled in self.enabled_nodes(node, suppress_live=True):
        if enabled in self.obstacles:
          unlocked.add(enabled)
    return unlocked
  def unlocked_abilities(self):
    """Print all of the abilities that can be placed."""
    unlocked = set()
    for node in self.net:
      for enabled in self.enabled_nodes(node, suppress_live=True):
        if enabled in self.abilities:
          unlocked.add(enabled)
    return unlocked
  def unlocked(self):
    """Print all of the nodes that can be placed."""
    return self.unlocked_abilities().union(self.unlocked_obstacles())
  def locked(self):
    """Print all of the nodes that can't be placed."""
    la = set(self.locked_abilities().keys())
    return la.union(self.locked_obstacles())
  def required(self, node):
    """What else needs to be placed in the graph before I
    can place node?
    """
    assert node in self.nodes
    reqs = self.nodes[node].reqs
    active = set(self.net.keys())
    unfilled = reqs - active
    if len(unfilled) > 0:
      print unfilled
    else:
      print "requirements for {} are satisfied already.".format(node)
  def speculate(self, ability, after='start'):
    """If I unlock ability, what new nodes are unlocked?"""
    new_net = copy.deepcopy(self)
    if len(self.nodes[ability].reqs) > 0:
      for node in self.net:
        pastbranch = self.past(node)
        if self.nodes[ability].enabled(pastbranch):
          after = node
          break
    new_net.add_connection(after, ability)

    old = self.unlocked().union(set(self.net.keys()))
    new = new_net.unlocked().union(set(new_net.net.keys()))
    return new - old
    # TODO: smarter exception handling here, suggest
    # where to place the node if it is eclipsed, for example
  def joint_obstacle(self, ability):
    """For ability that eclipses more than one other ability,
    determine a set of possible signatures for a joint obstacle
    that would enable ability in its future.
    """
    assert ability in self.abilities
    for req in self.nodes[ability].reqs:
      assert req in self.net
    sets = {r: set() for r in self.nodes[ability].reqs}
    for req in self.nodes[ability].reqs:
      sets[req].add(req)
      for node in self.net:
        if req in self.past(node):
          sets[req].add(node)
    return list(itertools.product(*sets.values()))
  def new_obstacles(self):
    """Determine which abilities indicate the need for a
    new joint obstacle.
    """
    # get all abilities with more than one requirement
    for ab in [n for n in self.abilities if len(self.nodes[n].reqs) > 1]:
      # check that all of its requirements are already placed
      reqs_met = [req in self.net for req in self.nodes[ab].reqs]
      if all(reqs_met):
        sets = self.joint_obstacle(ab)
        print '{} requires a joint obstacle, possibly with the following requirements:'.format(ab)
        for joint in sets:
          print joint
        print '\n'
      else:
        print '{} has multi requirements that are not yet placed\n'.format(ab)
    for ob in self.locked_obstacles():
      for req in self.nodes[ob].reqs:
        if isinstance(req, tuple):
          print 'or consider using {}: {}'.format(ob, req)
  def place_next(self):
    """Describe which things cane be placed next and what they
    would unlock.
    """
    # (unlocked) node A can be placed after B or C, and would unlock D, E, and F
    for ob in self.unlocked_obstacles():
      print 'obstacle {} can be placed anywhere'.format(ob)
      results = self.speculate(ob)
      if len(results) > 0:
        print ' and would unlock {}'.format(results)
      print '\n'
    for ab in self.unlocked_abilities():
      print 'ability {} can be placed '.format(ab)
      if len(self.nodes[ab].reqs) > 0:
        possible_spots = []
        for node in self.net:
          pastbranch = self.past(node)
          if self.nodes[ab].enabled(pastbranch):
            possible_spots.append(node)
        print 'after {}'.format(possible_spots)
      else:
        print 'anywhere'
      results = self.speculate(ab)
      if len(results) > 0:
        print ' and would unlock {}'.format(results)
      print '\n'
  def analyze(self):
    # locked abilities & locked obstacles
    # place next analysis: (unlocked) node A can be placed after B or C, and would unlock D, E, and F
    # required joint obstacles
    print 'LOCKED ABILITIES:\n'
    locked_abilities = self.locked_abilities()
    for key in locked_abilities:
      print '{}: {}'.format(key, locked_abilities[key])
    print '\n'
    print 'LOCKED OBSTACLES:\n'
    locked_obstacles = self.locked_obstacles()
    for key in locked_obstacles:
      print '{}: {}'.format(key, locked_obstacles[key])
    print '\n'
    print 'PLACE NEXT:\n'
    self.place_next()
    print 'JOINT OBSTACLE ANALYSIS:\n'
    self.new_obstacles()

  def nxgraph(self):
    """Return a NetworkX graph suitable for plotting"""
    dl = {}
    for key in self.net.keys():
        dl[key] = list(self.net[key])
    labels = [node for node in self.net]
    return nx.Graph(dl)
  def plot(self, spring=False):
    """Visualize the graph."""
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_axes([0.2, 0.2, 0.8, 0.8])

    g = self.nxgraph()
    if spring:
      pos=nx.networkx.spring_layout(g)
    else:
      pos=nx.networkx.spectral_layout(g)

    abilities = [node for node in self.abilities if node in self.net]
    obstacles = [node for node in self.obstacles if node in self.net]
    labels = {node:self.nodes[node].name for node in self.net}
    start_end = ['start']
    if 'end' in self.net:
      start_end.append('end')

    nx.draw_networkx_nodes(g, pos, nodelist=abilities, ax=ax,
                           alpha=0.5, node_size=500)
    nx.draw_networkx_nodes(g, pos, nodelist=obstacles, ax=ax,
                           node_color='b', alpha=0.5, node_size=500)
    nx.draw_networkx_nodes(g, pos, nodelist=start_end, ax=ax,
                           node_color='g', alpha=0.5, node_size=500)

    nx.draw_networkx_edges(g, pos, width=0.5, alpha=0.5, ax=ax)
    nx.draw_networkx_labels(g, pos, labels, ax=ax)

    ax.set_xticks([])
    ax.set_yticks([])
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    ax.set_xlim([xlim[0]*1.1, xlim[1]])
    ax.set_ylim([ylim[0]*1.1, ylim[1]])
    reddots = Line2D([0], [0], linestyle=None, linewidth=0, color='r', marker='o', alpha=0.5,
                     markeredgecolor=None, markeredgewidth=0.0)
    bluedots = Line2D([0], [0], linestyle=None, linewidth=0, color='b', marker='o', alpha=0.5,
                      markeredgecolor=None, markeredgewidth=0.0)
    ax.legend((reddots, bluedots),
              ("ability", "obstacle"),
              fontsize=12, numpoints=1, loc='lower left')

    plt.show(fig)
