import networkx as nx
from map_client import MapClient
import time

class Vehicle:
    def __init__(self, vehicle_id: int, source=None, destination=None, map_client: MapClient = None):
        self.id = vehicle_id
        self.source = source
        self.destination = destination
        self.map_client = map_client
        self.current_step = 0
        self.status = "stop"
        if source and destination and map_client:
            self.schedule()

    def change_status(self, status: str):
        """Change the status of the vehicle."""
        self.status = status
        # print(f"Vehicle {self.id}: Status changed to {self.status}")

    def get_current_node(self):
        """Get the current node in the path."""
        return self.path[self.current_step]
    
    def get_next_node(self):
        """Get the next node in the path."""
        if self.is_at_destination():
            return None
        return self.path[self.current_step + 1]
    
    def get_current_step(self):
        """Get the current step in the path."""
        return self.current_step

    def move(self):
        if self.get_next_node():
            time.sleep(1)  # Simulate time taken to move
            self.current_step += 1
            print(f"Vehicle {self.id}: Moving to node {self.path[self.current_step]} in path.")
        # else:
        # if self.is_at_destination():
        #     self.change_status("finished")
    
    def is_at_destination(self):
        """Check if the vehicle has reached its destination."""
        return (self.current_step == len(self.path) - 1)

    def schedule(self):
        if not self.map_client.maps:
            print("No maps available for pathfinding.")
            self.path = []
            return

        G = self.map_client.maps[0].to_networkx_graph()
        if G.number_of_nodes() == 0:
            print("Failed to create graph from map data.")
            self.path = []
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