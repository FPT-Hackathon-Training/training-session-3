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
    
    def check_potential_collision(self):
        paths = [vehicle.path for vehicle in self.vehicles.values() if vehicle.path]
        min_length = min(len(path) for path in paths) if paths else 0
        
        if len(paths) < 2:
            print("Not enough vehicles to check for collisions.")
            return []
        
        for i in range(min_length):
            if paths[0][i] == paths[1][i]:
                self.collision_info.append((i, paths[0][i]))
        
        if self.collision_info:
            self.collision_detected = True
