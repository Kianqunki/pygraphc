import networkx as nx
import sys
from collections import deque
from itertools import chain, islice, combinations

class kclique_percolation_bruteforce:
	def __init__(self, g, k, threshold):
		self.g = g
		self.k = k
		self.threshold = threshold
		print 'kclique_percolation: initialization ...'
	
	def enumerate_all_cliques(self):
		# https://networkx.github.io/documentation/development/_modules/networkx/algorithms/clique.html#enumerate_all_cliques
		print 'enumerate_all_cliques ...'
		index = {}
		nbrs = {}
		for u in self.g:
			sys.stdout.write('.')
			index[u] = len(index)
			# Neighbors of u that appear after u in the iteration order of G.
			nbrs[u] = {v for v in self.g[u] if v not in index}

		queue = deque(([u], sorted(nbrs[u], key=index.__getitem__)) for u in self.g)
		# Loop invariants:
		# 1. len(base) is nondecreasing.
		# 2. (base + cnbrs) is sorted with respect to the iteration order of G.
		# 3. cnbrs is a set of common neighbors of nodes in base.
		while queue:
			sys.stdout.write('.')
			base, cnbrs = map(list, queue.popleft())
			yield base
			for i, u in enumerate(cnbrs):
				# Use generators to reduce memory consumption.
				queue.append((chain(base, [u]),
							  filter(nbrs[u].__contains__,
									 islice(cnbrs, i + 1, None))))
	
	def get_geometric_mean(self, weights):		
		multiplication = 1
		for weight in weights:
			multiplication = multiplication * weight
		
		gmean = 0.0
		multiplication = round(multiplication, 5)			
		if multiplication > 0.0:		
			k = float(len(weights))
			gmean = multiplication ** (1 / k)
			
		return round(gmean, 5)
		
	def find_weighted_kclique(self):		
		print 'find_weighted_kclique ...'		
		cliques = list(self.enumerate_all_cliques())	
		k_cliques = [clique for clique in cliques if len(clique) == self.k]		
		valid_cliques = []	
		for clique in k_cliques:				
			weights = []
			for u, v in combinations(clique, 2):										
				reduced_precision = round(self.g[u][v][0]['weight'], 5)
				weights.append(reduced_precision)				
			gmean = self.get_geometric_mean(weights)	
			if gmean > self.threshold:
				valid_cliques.append(frozenset(clique))
			
		return valid_cliques
	
	def get_kclique_percolation(self):
		print 'get_kclique_percolation ...'
		cliques = self.find_weighted_kclique()		
		percolation_graph = nx.Graph()
		percolation_graph.add_nodes_from(cliques)
		
		# Add an edge in the percolation graph for each pair of cliques that percolate
		for clique1, clique2 in combinations(cliques, 2):		
			if len(clique1.intersection(clique2)) >= (self.k - 1):
				percolation_graph.add_edge(clique1, clique2)
		
		# Get all connected component in percolation graph
		kclique_percolation = []
		for component in nx.connected_components(percolation_graph):			
			kclique_percolation.append(frozenset.union(*component))
			
		return kclique_percolation	
