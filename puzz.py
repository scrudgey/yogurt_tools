# -*- coding: utf-8 -*-
"""Yogurt commercial puzzle planning code
Using graph theory to plan out the order of puzzles and abilities.
"""
import networkx as nx
import collections
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
      # print overlaps
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
    if branch in self.obstacles:
      for ability in self.abilities.values():
        pastbranch = self.past(branch)
        if ability.enabled(pastbranch):
          enableds[ability.name] = ability.enablers(pastbranch)
    if suppress_live:
      placed_nodes = [node for node in enableds if self.nodes[node].placed]
      for node in placed_nodes:
        enableds.pop(node, None)
    return enableds
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
