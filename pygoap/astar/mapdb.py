# -*- coding: utf-8 -*-

"""
This is the fundemental base that the mapping suite uses to abstract
a map.  feel free to overload.  the most basic functionality must be that
the object can relate objects to eachother.  that is all.

should the db hold instances of objects, or their hashes?..or references?  =)

currently this has an extra attribute added "mw", this needs to be more generic

"""

__version__ = "memdb v.008"

class MapNode(object):
	"""The most basic element of a map.

	In general, the node does not need specific coordinates, only relative
	to other nodes.  (surrounding)
	The id should be unique
	"""
	def __init__(self, nodeID=None):
		self.id = nodeID

	def __repr__(self):
		return "<MapNode ID: %s>" % (self.id)

class MapDB(object):
	"""
	This abstract class is a foundation for all the modules as part of
	the automapper.  Please extend this class to make it more useful.  ;)
	"""
	def _get_next_ID(self):
		"""Return a unique number.
		"""
		raise NotImplementedError

	def clear(self):
		"""Clear the map of all data
		"""
		raise NotImplementedError

	def get_nodes(self):
		"""Return a tuple of nodes in the database.
		"""
		raise NotImplementedError

	def create_node(self):
		"""Create new node in the database and return the node object.
		"""
		raise NotImplementedError

	def add_node(self, node, surr=[]):
		"""Add an existing node object to the database.
		"""
		raise NotImplementedError

	def remove_node(self, node):
		"""Remove the node from the database.
		"""
		raise NotImplementedError

	def connect_node(self, node1, node2):
		"""Connect the two nodes.
		"""
		raise NotImplementedError

	def connect_node2(self, node1, node2, mw):
		"""Connect the two nodes with the given mw (magic word).
		"""
		raise NotImplementedError

	def disconnect_node(self, node1, node2):
		"""Disconnect the two nodes.
		"""
		raise NotImplementedError

	def get_magicword(self, node1, node2):
		"""Return the magicword for this node pair
		"""
		raise NotImplementedError

	def set_magicword(self, node1, node2, mw):
		"""Set the mw associated with the node pair.

		Should raise ValueError if the node pair is not in database.
		"""
		raise NotImplementedError

	def get_surrounding(self, node):
		"""Return a tuple of nodes that are surrounding the given node.
		"""
		raise NotImplementedError

	def set_surrounding(self, node, neighbors):
		"""Overwrite the surrounding of node.

		Should be a list of objects.
		"""
		raise NotImplementedError

	def get_surrounding2(self, node):
		"""Return a tuple of (node, mw) pairs of surroounding nodes.
		"""
		raise NotImplementedError

	def set_surrounding2(self, node, neighbors):
		"""Overwrite the surrounding of node.

		Should be a list of (objects, mw) pairs.
		"""
		raise NotImplementedError

import cPickle as pickle
from types import TupleType

class MemoryDB(MapDB):
	"""This class will provide a map in memory using lists and a dict.

	currently, nodes can be added, but not removed individually!

	Should be quite fast.
	Two new methods, save and load, allow the database to be saved via pickle.
	"""
	def __init__(self, name="unnamed"):
		self.name = name

		self._connections = {}
		self._nextID = 0
		self._dirty = False

	def _get_next_ID(self):
		self._nextID += 1
		self._dirty = True
		return self._nextID

	def clear(self):
		self._connections = {}
		self._nextID = 0
		self._dirty = True

	def get_nodes(self):
		return tuple(self._connections.keys())

	def add_node(self, node, surr=None):
		if surr == None:
			self._connections[node] = []
		else:
			self._connections[node] = surr
		self._dirty = True

	def create_node(self, nodeID=None):
		if nodeID == None:
			nodeID = str(self._get_next_ID())

		#sanity check
		if nodeID in [x.id for x in self.get_nodes()]:
			raise ValueError

		node = MapNode(nodeID)
		self.add_node(node)
		self._dirty = True
		return node

	def connect_node(self, node1, node2):
		self._connections[node1].append(node2)
		self._dirty = True

	def get_surrounding(self, node):
		return tuple(self._connections[node])

	def set_surrounding(self, node, surr):
		# We *could* put more check to verify that data conforms the format...
		try:
			self._connections[node] = surr
		except ValueError:
			self.add_node(node, surr)

	def get_surrounding3(self, node, finish):
		# return a list of nodes with a cost
		# (node, cost, h)
		# costs not implimented, just send a 1
		# huerstics not implimented, just send a 1

		surrounding=[]
		for node2 in self._connections[node]:
			surrounding.append((node2, 1, 1))
		return tuple(surrounding)

	def save(self):
		saveFile = file(self.name + '.pickle', 'w')
		pickle.dump(self._connections, saveFile)
		saveFile.close()
		self._dirty = False

	def load(self):
		saveFile = file(self.name+'.pickle', 'r')
		self._connections = pickle.load(saveFile)
		saveFile.close()
		self._dirty = True

class MemoryMudDB(MemoryDB):
	"""This class will provide a map in memory using lists and a dict.

	gear'd for the "surrounding2" methods with provide methods for muds
		-- includes "magic words"
	"""
	def connect_node2(self, node1, node2, mw):
		self._connections[node1].append((node2, mw))
		self._dirty = True

	def get_surrounding2(self, node):
		return tuple(self._connections[node])

	def set_surrounding2(self, node, surr):
		# We *could* put more check to verify that data conforms the format...
		if node not in self._connections:
			raise ValueError

		if type(surr[0]) != TupleType:
			raise ValueError

		self._connections[node] = surr
		self._dirty = True

	def get_surrounding3(self, node, finish):
		# return a list of nodes with a cost
		# (node, cost, h)
		# costs not implimented, just send a 1
		# huerstics not implimented, just send a 1
		surrounding=[]
		for node2, mw in self._connections[node]:
			surrounding.append((node2, 1, 1))

		return tuple(surrounding)

class TestDB(MemoryMudDB):
	"""Class that is populated with a basic map for tesing.
	"""
	def __init__(self):
		MemoryMudDB.__init__(self, "test")
		self.made = {}
		map(self._get_connection, self._get_data())
		del self.made
		#del self._get_connection
		#del self._get_node
		#del self._get_data

	def _get_connection(self, conn):
		func = self._get_node
		self.connect_node2(func(conn[0]), func(conn[1]), conn[2])

	def _get_node(self, node_ID):
		try:
			node = self.made[node_ID]
		except KeyError:
			node = self.create_node(node_ID)
			self.made[node_ID] = node
		return node

	def _get_data(self):
		raw_data = """
			A B S
			B C E
			C D S
			D E E
			E F E
			F G N

			D J S
			J H E
			F H S
			H I E
			L A S
			M L S

			N M E
			O M W
			I P E
			Q P S
			R Q S

			R G W
			N S S
			T J N

			B U W
			U V W
			V W W
			W X W
			X Y S
			Y Z E



			B A N
			C B W
			D C N
			E D W
			F E W

			G F S
			G C W
			J D N
			H J W
			H F N

			I H W
			A L N
			L M N
			M N W
			M O E

			P I W
			P Q N
			Q R N
			G R E
			S N N
			J T S

			U B E
			V U E
			W V E
			X W E
			Y X N
			Z Y W

		""".split()

		data = [raw_data[x:x+3] for x in range(0, len(raw_data), 3) ]
		return data
