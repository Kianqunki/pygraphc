from math import log
from ClusterUtility import ClusterUtility


class GraphEntropy(object):
    """A class for graph clustering using entropy-based method [Kenley2011]_. The review of
       some graph clustering method for PPI networks, including this entropy-based, was presented in [Price2013]_.
       This code is NetworkX version of the original code by True Price [Price2016]_.

    References
    ----------
    .. [Kenley2011] Edward Casey Kenley and Young-Rae Cho, Detecting protein complexes and functional modules
                    from protein interaction networks: A graph entropy approach,
                    Proteomics 2011, 11, pp. 3835-3844.
    .. [Price2013]  True Price, Francisco I Pena III, Young-Rae Cho, Survey: Enhancing Protein Complex Prediction in
                    PPI Networks with GO Similarity Weighting, Interdisciplinary Sciences: Computational Life Sciences,
                    5(3), pp. 196-210, 2013.
    .. [Price2016]  True Price, Graph clustering in Python, https://github.com/trueprice/python-graph-clustering.
    """
    def __init__(self, graph):
        """The constructor for class GraphEntropy.

        Parameters
        ----------
        graph   : graph
            A graph to be clustered.
        """
        self.graph = graph

    def get_graph_entropy(self):
        """The main method to execute clustering based on graph entropy.

        Returns
        -------
        clusters    : dict[list]
            Dictionary of list containing nodes for each cluster.
        """
        nodes = set(self.graph.nodes())
        clusters = {}
        cluster_id = 0

        while nodes:
            seed_node = nodes.pop()
            cluster_candidate = set(self.graph.neighbors(seed_node))
            cluster_candidate.add(seed_node)
            entropies = self._get_entropies(cluster_candidate, self.graph.nodes())

            # removing neighbors to minimize entropy
            for node in list(cluster_candidate):
                if node == seed_node:   # don't remove the seed node
                    continue

                new_cluster = cluster_candidate.copy()
                new_cluster.remove(node)
                new_entropies = self._get_entropies(new_cluster, self.graph.neighbors(node))

                if sum(new_entropies.itervalues()) < sum(entropies[v] for v in self.graph.neighbors(node)):
                    cluster_candidate = new_cluster
                    entropies.update(new_entropies)

            # boundary candidates, a intersection with b
            c = reduce(lambda a, b: a | b, (set(self.graph.neighbors(v)) for v in cluster_candidate)) - \
                cluster_candidate

            while c:
                node = c.pop()
                new_cluster = cluster_candidate.copy()
                new_cluster.add(node)
                new_entropies = self._get_entropies(new_cluster, self.graph.neighbors(node))

                if sum(new_entropies.itervalues()) < sum(entropies[v] for v in self.graph.neighbors(node)):
                    cluster_candidate = new_cluster
                    entropies.update(new_entropies)
                    c &= set(self.graph.neighbors(node)) - cluster_candidate

            nodes -= cluster_candidate

            if len(cluster_candidate) > 0:
                clusters[cluster_id] = list(cluster_candidate)
                cluster_id += 1
                # print '-'.join(str(c) for c in cluster_candidate)

        ClusterUtility.set_cluster_id(self.graph, clusters)
        return clusters

    def _get_entropies(self, cluster_candidate, neighbors):
        """Get entropy from cluster candidate or all nodes in a graph.

        Parameters
        ----------
        cluster_candidate   : iterable
            The entity to be analyzed for its entropy. It can be cluster candidate or a graph.
        neighbors           : list
            The neigbors of processed node.

        Returns
        -------
        entropies   : dict
            Dictionary of entropies. Key: node identifier and value: entropy.
        """
        entropies = {}
        for node in neighbors:
            entropies[node] = self._get_node_entropy(cluster_candidate, node)

        return entropies

    def _get_node_entropy(self, cluster_candidate, node):
        """Get node's entropy.

        Parameters
        ----------
        cluster_candidate   : set
            The entity to be analyzed for its entropy. It can be cluster candidate or a graph.
        node                : int
            The analyzed node to be calculated for its entropy.

        Returns
        -------
        entropy : float
            Entropy for a particular node.
        """
        # get node degree with weight
        degree = self.graph.degree(weight='weight')[node]
        if degree == 0:
            return 0

        # get inner link/edge probability
        neighbors_weight = self.graph[node]
        neighbors_weight_sum = 0
        for node_id, weight in neighbors_weight.iteritems():
            if node_id in cluster_candidate:
                neighbors_weight_sum += weight[0]['weight']
        inner_probability = neighbors_weight_sum / degree

        # get entropy
        entropy = 0 if inner_probability <= 0.0 or inner_probability >= 1.0 else \
            -inner_probability * log(inner_probability, 2) - (1 - inner_probability) * log(1 - inner_probability, 2)

        return entropy