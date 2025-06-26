from typing import List, Optional
import requests
from map import Map
from rich.console import Console

class MapClient:
    """Client for fetching map data from the server"""
    def __init__(self, base_url: str = "https://hackathon.omelet.tech/api/maps/"):
        self.base_url = base_url
        self.maps = []

    def fetch_maps(self, console: Console) -> Optional[List[Map]]:
        """Fetch all maps from the server"""
        console.print("[bold yellow]Fetching map data from server...[/bold yellow]")
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            data = response.json()
            
            if 'results' in data:
                self.maps = [Map(map_data) for map_data in data['results'][:1]]
                console.print(f"[bold green]✓ Successfully fetched {len(self.maps)} map(s)[/bold green]\n")

                self.destinationPositions = data['results'][0].get('destination_positions', [])
                self.startingPositions = data['results'][0].get('starting_positions', [])

                return True
            else:
                console.print("[bold red]✗ No map data found in response[/bold red]")
                return False

        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]✗ Error fetching data: {e}[/bold red]")
            return False

    def visualize_map(self, console: Console):
        """Visualize the fetched maps"""
        if self.maps:
            # Print detailed information for each map
            for i, map_obj in enumerate(self.maps):
                console.print(f"\n[bold blue]═══ Map {i+1} of {len(self.maps)} ═══[/bold blue]\n")
                map_obj.print_graph_info(console)
                console.print("\n" + "─" * 50 + "\n")

        else:
            console.print("[bold red]✗ Failed to fetch map data or no maps available[/bold red]")