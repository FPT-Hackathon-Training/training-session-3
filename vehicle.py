import networkx as nx
from map_client import MapClient

class Vehicle:
    def __init__(self, vehicle_id: int, source=None, destination=None, map_client: MapClient = None):
        self.id = vehicle_id
        self.source = source
        self.destination = destination
        self.current_position = 0
        self.map_client = map_client
        self.path = []
        if source and destination:
            self.schedule()

    def get_next_node(self):
        """Get the next node in the path."""
        if not self.path:
            print(f"Vehicle {self.id}: No path available.")
            return None
        if self.current_position < len(self.path):
            next_node = self.path[self.current_position]
            self.current_position += 1
            return next_node
        else:
            print(f"Vehicle {self.id}: Reached the end of the path.")
            return None

    def schedule(self):
        if not self.map_client.maps:
            print("No maps available for pathfinding.")
            return

        G = self.map_client.maps[0].to_networkx_graph()
        if G.number_of_nodes() == 0:
            print("Failed to create graph from map data.")
            return

        if self.source not in G or self.destination not in G:
            print(f"Source {self.source} or destination {self.destination} not in graph.")
            self.path = []
            return

        try:
            path = nx.shortest_path(G, source=self.source, target=self.destination, weight="weight")
            weight = sum(G[u][v]['weight'] for u, v in zip(path[:-1], path[1:]))
            self.path = path
            print(f"Vehicle {self.id}: shortest path from {self.source} to {self.destination}: {path} with total weight: {weight}")

        except (nx.NetworkXNoPath, nx.NodeNotFound) as e:
            self.path = []
            print(f"Vehicle {self.id}: Error finding path: {e}")