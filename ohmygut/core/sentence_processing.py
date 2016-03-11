# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import networkx as nx
import re


class SentenceParser(object):
    def __init__(self, stanford_dependency_parser):
        self.stanford_dependency_parser = stanford_dependency_parser

    def parse_sentence(self, sentence):
        try:
            dependency_graph_iterator = self.stanford_dependency_parser.raw_parse(sentence)
        except OSError:
            return
        
        dependency_graph = next(dependency_graph_iterator)

        nodes = [node for node in dependency_graph.nodes.keys() if node]
        edges = [
            (n, dependency_graph._hd(n), {'rel': dependency_graph._rel(n)})
            for n in nodes if dependency_graph._hd(n)
            ]

        nx_graph = nx.DiGraph()
        nx_graph.add_nodes_from(nodes)
        nx_graph.add_edges_from(edges)

        words = {node: dependency_graph.nodes[node]['word'] for node in nodes}
        tags = {node: dependency_graph.nodes[node]['tag'] for node in nodes}

        return ParserOutput(nx_graph=nx_graph,
                            words=words,
                            tags=tags)


class ParserOutput(object):
    def __init__(self, nx_graph, words, tags):
        self.nx_graph = nx_graph
        self.words = words
        self.tags = tags

    def draw(self):
        G = self.nx_graph.to_undirected()
        pos = nx.spring_layout(G)

        nx.draw_networkx_nodes(G, pos, node_size=1000, node_color='white')
        nx.draw_networkx_edges(G, pos, width=6, alpha=0.5, edge_color='black')
        nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif',
                                labels=self.words
                                )
        nx.draw_networkx_edge_labels(G, pos, font_size=10,
                                     edge_labels=dict(((i, j), G[i][j]['rel']) for i, j in G.edges())
                                     )
        plt.axis('off')
        plt.show()
