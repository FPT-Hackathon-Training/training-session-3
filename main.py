from map_client import MapClient
from rich.console import Console
from vehicle import Vehicle
from vehicle_manager import VehicleManager

def main():
    console = Console()
    client = MapClient()

    client.fetch_maps(console)
    
    if client.fetch_maps(console):
        client.visualize_map(console)
    else:
        console.print("[bold red]✗ Failed to fetch or visualize maps[/bold red]")

    v1 = Vehicle(vehicle_id=1, source=4, destination=2, map_client=client)
    v2 = Vehicle(vehicle_id=2, source=6, destination=2, map_client=client)

    vehicle_manager = VehicleManager()
    vehicle_manager.add_vehicle(v1.id, v1)
    vehicle_manager.add_vehicle(v2.id, v2)

    vehicle_manager.check_potential_collision()

if __name__ == "__main__":
    main()
