class VehicleManager:
    def __init__(self):
        self.vehicles = {}
        self.vehicles_ready = False
        self.collision_detected = False
        self.collision_info = []

    def add_vehicle(self, vehicle_id, vehicle_data):
        """Add a new vehicle."""
        if vehicle_id in self.vehicles:
            raise ValueError(f"Vehicle {vehicle_id} already exists.")
        self.vehicles[vehicle_id] = vehicle_data
        if len(self.vehicles) == 2:
            self.vehicles_ready = True

    def remove_vehicle(self, vehicle_id):
        """Remove an existing vehicle."""
        if vehicle_id not in self.vehicles:
            raise ValueError(f"Vehicle {vehicle_id} does not exist.")
        del self.vehicles[vehicle_id]

    def get_vehicle(self, vehicle_id):
        """Retrieve a vehicle's data."""
        return self.vehicles.get(vehicle_id, None)

    def list_vehicles(self):
        """List all vehicles."""
        return list(self.vehicles.keys())
    
    def schedule_vehicles(self):
        """Schedule paths for all vehicles."""

        if self.all_waiting():
            next_nodes = [vehicle.get_next_node() for vehicle in self.vehicles.values()]

            if next_nodes[0] != next_nodes[1]:
                for vehicle in self.vehicles.values():
                    vehicle.change_status("moving")
                    vehicle.move()
                return 2

            else:
                v1 = list(self.vehicles.values())[0]
                v1.change_status("moving")
                v1.move()
                return 1
        
        else:
            for vehicle in self.vehicles.values():
                if vehicle.status == "waiting":
                    vehicle.change_status("moving")
                    vehicle.move()
            return 1
        return 0
            
    def is_complete(self):
        """Check if all vehicles have reached their destination."""
        return all(vehicle.is_at_destination() for vehicle in self.vehicles.values())
    
    def all_waiting(self):
        """Check if all vehicles are waiting."""
        return all(vehicle.status == "waiting" for vehicle in self.vehicles.values())
    
    def has_moving_vehicle(self):
        """Check if there is at least one vehicle moving."""
        return any(vehicle.status == "moving" for vehicle in self.vehicles.values())

    def check_potential_collision(self):
        paths = [vehicle.path for vehicle in self.vehicles.values() if vehicle.path]
        min_length = min(len(path) for path in paths) if paths else 0
        
        if len(paths) < 2:
            print("Not enough vehicles to check for collisions.")
            return []
        
        # Assuming that only two vehicles are registered for collision detection
        for i in range(min_length):
            if paths[0][i] == paths[1][i]:
                self.collision_info.append((i, paths[0][i]))
        
        if self.collision_info:
            self.collision_detected = True
