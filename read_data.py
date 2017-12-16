import numpy as np
import matplotlib.pyplot as plt
import re
import os
from collections import namedtuple
from collections import Counter
from operator import attrgetter
from sets import Set

Event = namedtuple('Event', ['id', 'name', 'desc', 'disturbing', 'disgusting', 'chaos', 'offensive', 'positive'])

def read_data(prepend=None):
  filename = 'commercial_events.txt'
  if prepend:
    filename = os.path.join(prepend, filename)
  with open(filename) as f:
    lines = f.readlines()
  filename = 'commercial_history.txt'
  if prepend:
    filename = os.path.join(prepend, filename)
  with open(filename) as f:
    history = [line.rstrip() for line in f.readlines()]
  parser = re.compile('(\D+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)')
  events = []
  for index, (line, what) in enumerate(zip(lines, history)):
    m = parser.match(line)
    events.append(Event(index, m.group(1), what, int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(6))))
  return events, history

def timeline(events):
  fig = plt.figure(figsize=(10, 10))
  ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
  ax.plot([event.disturbing for event in events], marker='o', label='disturbing')
  ax.plot([event.disgusting for event in events], marker='o', label='disgusting')
  ax.plot([event.chaos for event in events], marker='o', label='chaos')
  ax.plot([event.offensive for event in events], marker='o', label='offensive')
  ax.plot([event.positive for event in events], marker='o', label='positive')
  ax.legend()
  plt.show(fig)

def maxes(events):
  keys = ['disturbing', 'disgusting', 'chaos', 'offensive', 'positive']
  for key in keys:
    event = max(events, key=attrgetter(key))
    print 'most {}: {}: when {} ({}) {}'.format(key, event.id, event.desc, event.name, attrgetter(key)(event))

def hist(events):
  noun_counts = Counter([event.name for event in events])
  labels, values = zip(*noun_counts.most_common())
  total = sum(noun_counts.values())
  values = [value/(1.0*total) for value in values]
  pos = np.arange(len(labels))+.5
  fig = plt.figure(figsize=(10, 10))
  ax = fig.add_axes([0.3, 0.1, 0.6, 0.8])
  ax.barh(pos, values, align='center')
  ax.set_yticks(pos)
  ax.set_yticklabels(labels)
  ax.invert_yaxis()
  ax.set_xlabel('Percentage')
  plt.show(fig)

def highestn(events, n=3):
  count = Counter()
  deltas = []
  note = []
  for key in ['disturbing', 'disgusting', 'chaos', 'offensive', 'positive']:
    print 'Top {} most {}'.format(n, key)
    sort = sorted(events, key=attrgetter(key))[::-1]
    f = attrgetter(key)
    for i in range(n):
      print '{}: {}'.format(i, sort[i].desc)
      count.update([sort[i].id])
      deltas.append(f(sort[i])-f(sort[i+1]))
      note.append(sort[i])
    print ''

  print 'notable events'
  for i, _ in count.most_common(3):
    event = events[i]
    print '{}: {}'.format(event.name, event.desc)
  print ''

  print 'notable deltas'
  sort = sorted(zip(deltas, note))[::-1]
  notable = Set()
  i = 0
  while len(notable) < 3:
    notable.add(sort[i][1])
    i += 1
  for event in notable:
    print '{}: {}'.format(event.name, event.desc)
  print ''
  for d, n in zip(deltas, note):
    print d, n.desc
  print ''

  print 'most common events'
  noun_counts = Counter([event.name for event in events])
  labels, values = zip(*noun_counts.most_common(3))
  for label, value in zip(labels, values):
    print '{}: {}'.format(label, value)

def cumplot(events):
  fig = plt.figure(figsize=(10, 10))
  ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
  keys = ['disturbing', 'disgusting', 'chaos', 'offensive', 'positive']
  for key in keys:
    f = attrgetter(key)
    x = [f(event) for event in events]
    cum = np.cumsum(x)/(1.0*sum(x))
    ax.plot(cum, label=key)
  ax.legend(loc='upper left')
  plt.show(fig)

def pie(events):
  noun_counts = Counter([event.name for event in events])
  labels, values = zip(*noun_counts.items())
  fig = plt.figure(figsize=(10, 10))
  ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
  ax.pie(values, labels=labels)
  plt.show(fig)
