from pygraphc.clustering.ClusterUtility import ClusterUtility
from pygraphc.clustering.ClusterAbstraction import ClusterAbstraction
import csv


class AnomalyScore(object):
    def __init__(self, graph, clusters, filename):
        self.graph = graph
        self.clusters = clusters
        self.filename = filename
        self.property = {}
        self.abstraction = {}

    def write_property(self):
        # get cluster abstraction and its properties
        self.abstraction = ClusterAbstraction.dp_lcs(self.graph, self.clusters)
        self.property = ClusterUtility.get_cluster_property(self.graph, self.clusters)

        # write to csv
        f = open(self.filename + '_anomaly.csv', 'wt')
        writer = csv.writer(f)

        # set header
        header = ('cluster_id', 'cluster_abstraction') + tuple(self.property[0].keys())
        writer.writerow(header)

        # write data
        for cluster_id, abstract in self.abstraction.iteritems():
            row = (cluster_id, abstract) + tuple(self.property[cluster_id].values())
            writer.writerow(row)