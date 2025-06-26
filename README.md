# Training session 3

## Description
- This project simulates vehicle motion and identifies possible collisions as two vehicles move across a map.
- All core functionality is implemented in `main.py`

## Setup
### Install Required Python Packages
```bash
pip install -r requirements.txt
```
### How to run
Run server
```bash
python simple_server.py
```
Run Client
```bash
python simple_client.py v1 6 2
```
## Homework

1. Collision handling occurs when 2 vehicles occupy the same edge
2. Develop a strategy to send control commands to vehicles at each time step, ensuring they reach their destinations safely without collisions.
- Modify the existing pathfinding algorithm to use an alternative to the original shortest path approach.
- Introduce a delay so that one car starts before the other, helping to prevent collisions.
- Continuously monitor the current and upcoming positions of the vehicles at each time step; if a collision is detected at a node or along an edge, set one vehicle to standby while allowing the other.