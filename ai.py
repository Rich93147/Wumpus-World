"""
  Wumpus World

  Class Attribute:
    SIZE = 4

  Public Attributes:
    observation -> the player's current perception as a list
      Order: [Stench, Breeze, Glitter, Bump, Scream]

    moves -> a list of the moves taken so far. First move is at index 0

    facing -> the players facing as an (x, y) tuple
    Facing (0, 1) -> up
      1, 0 === "right"
      0, 1 === "up"
      -1, 0 === "left"
      0, -1 === "down"

    player_loc  -> the players location as an (x, y) tuple

    start_loc   -> player starting location (1, 1)

    has_gold    -> True/False

    ammo        -> 1 or 0

    You should only need these attributes.

    Possible Actions: "forward", "left", "right", "grab", "climb", "shoot"
"""

from wumpus import WumpusWorld
from random import choice
from queue import PriorityQueue

# Knowledge base
observations = dict()
safe_rooms = {(1, 1)}
possible_wumpus_loc = set()
possible_pit_loc = set()
possible_gold = set((i, j) for i in range(1, 5) for j in range(1, 5))

target_square = None
action_queue = list()
wumpus_alive = True
returning_home = False

STENCH = 0
BREEZE = 1
GLITTER = 2


def distance(a: tuple, b: tuple) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def adjacent_rooms(loc: tuple) -> set:
    x, y = loc
    rooms = set()
    if x > 1:
        rooms.add((x - 1, y))
    if x < 4:
        rooms.add((x + 1, y))
    if y > 1:
        rooms.add((x, y - 1))
    if y < 4:
        rooms.add((x, y + 1))
    return rooms

def choose_closest_safe_room(world: WumpusWorld) -> tuple:
    candidates = safe_rooms.difference(set(observations.keys()))
    print(f"Safe rooms to choose from: {safe_rooms}")
    print(f"Candidates: {candidates}")
    if candidates:
        return min(candidates, key=lambda x: distance(world.player_loc, x))
    # If no unexplored safe rooms, return closest safe room
    return min(safe_rooms, key=lambda x: distance(world.player_loc, x))

# A* pathfinding algorithm
def find_path(room1: tuple, room2: tuple) -> list[tuple]:
    def heuristic(room):
        return distance(room, room2)

    open_set = PriorityQueue()
    open_set.put((0, room1))

    came_from = {}
    g_score = {room1: 0}
    f_score = {room1: heuristic(room1)}
    visited = set()

    while not open_set.empty():
        current = open_set.get()[1]

        if current == room2:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(room1)
            path.reverse()
            return path

        visited.add(current)

        for neighbor in adjacent_rooms(current).intersection(safe_rooms):
            if neighbor in visited:
                continue
            tentative_g = g_score[current] + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor)
                open_set.put((f_score[neighbor], neighbor))

    return []

def get_direction_to_neighbor(current: tuple, neighbor: tuple) -> tuple:
    # Returns the direction the player needs to face to go to the neighboring room
    dx = neighbor[0] - current[0]
    dy = neighbor[1] - current[1]
    return (dx, dy)

def turns_needed(current_facing: tuple, target_facing: tuple) -> list:
    # Returns number of turns needed to face target direction, so as to not overshoot
    if current_facing == target_facing:
        return []
    
    # Try turning right
    right_facing = (current_facing[1], -current_facing[0])
    if right_facing == target_facing:
        return ["right"]
    
    # Try turning left
    left_facing = (-current_facing[1], current_facing[0])
    if left_facing == target_facing:
        return ["left"]
    
    # Need to turn around
    return ["right", "right"]

def list_actions_to_square(world: WumpusWorld, target_square: tuple) -> list:
    # List of actions needed to move from current room to target room
    path = find_path(world.player_loc, target_square)
    
    if not path or len(path) < 2:
        return []
    
    actions = []
    current_facing = world.facing
    
    # Start from index 1 since path[0] is current location
    for i in range(1, len(path)):
        next_room = path[i]
        current_room = path[i - 1]
        
        # Determine direction to next room
        direction = get_direction_to_neighbor(current_room, next_room)
        
        # Add turns if needed
        turns = turns_needed(current_facing, direction)
        actions.extend(turns)
        
        # Update facing after turns
        current_facing = direction
        
        # Move forward
        actions.append("forward")
    
    return actions

def update_knowledge(world: WumpusWorld):
    # Update KB
    global observations
    global safe_rooms
    global possible_wumpus_loc
    global possible_pit_loc
    global possible_gold
    global wumpus_alive
    
    current_loc = world.player_loc
    obs = world.observation
    observations[current_loc] = obs
    
    # If scream (he dead af), clear wumpus loc, move old possible wumpus location to safe rooms
    if obs[4] == "Scream":
        wumpus_alive = False
        for room in possible_wumpus_loc:
            safe_rooms.add(room)
        possible_wumpus_loc.clear()
    
    # Get adjacent rooms
    adjacent = adjacent_rooms(current_loc)
    
    # If no stench and no breeze, all adjacent rooms are safe
    if obs[STENCH] == "None" and obs[BREEZE] == "None":
        safe_rooms.update(adjacent)
        # Remove these from hazard possibilities
        possible_wumpus_loc -= adjacent
        possible_pit_loc -= adjacent
    
    # Handle stench observations
    if obs[STENCH] == "Stench" and wumpus_alive:
        unvisited_adjacent = adjacent - set(observations.keys())
        if not possible_wumpus_loc:
            # First stench: wumpus is in one of these adjacent rooms
            possible_wumpus_loc.update(unvisited_adjacent)
        else:
            # Multiple stenches: wumpus prolly in intersection
            possible_wumpus_loc &= adjacent
    elif obs[STENCH] == "None":
        # No stench means no wumpus in adjacent rooms
        possible_wumpus_loc -= adjacent
    
    # Handle breeze observations
    if obs[BREEZE] == "Breeze":
        unvisited_adjacent = adjacent - set(observations.keys())
        if not possible_pit_loc:
            # First breeze: pit(s) could be in any of these adjacent rooms
            possible_pit_loc.update(unvisited_adjacent)
        else:
            # Update possible pit locations
            possible_pit_loc.update(unvisited_adjacent)
    elif obs[BREEZE] == "None":
        # No breeze means def no pits in adjacent rooms
        possible_pit_loc -= adjacent
    
    # Narrowing down pit locations in case of multiple pits around each other
    # Find which combos explain multiple breezes
    breeze_locations = [loc for loc, o in observations.items() if o[BREEZE] == "Breeze"]
    no_breeze_locations = [loc for loc, o in observations.items() if o[BREEZE] == "None"]
    
    if breeze_locations:
        all_rooms = set((i, j) for i in range(1, 5) for j in range(1, 5))
        valid_pit_locs = set()

        for candidate in all_rooms - set(observations.keys()):
            # Not adjancent to no breeze rooms
            is_valid = True
            for no_breeze_loc in no_breeze_locations:
                if candidate in adjacent_rooms(no_breeze_loc):
                    is_valid = False
                    break
            
            # Adjacent to atleast one breeze
            if is_valid:
                is_adjacent_to_breeze = any(candidate in adjacent_rooms(b_loc) for b_loc in breeze_locations)
                if is_adjacent_to_breeze:
                    valid_pit_locs.add(candidate)
        
        # Update possible pit locations to only valid ones
        if valid_pit_locs:
            possible_pit_loc &= valid_pit_locs
        
        # If a breeze can only be linked to one possible pit, adjacent rooms are dafe
        for breeze_loc in breeze_locations:
            adjacent_to_breeze = adjacent_rooms(breeze_loc)
            unvisited_adj = adjacent_to_breeze - set(observations.keys())
            possible_pits_here = unvisited_adj & possible_pit_loc
            
            # If only one possible pit can explain this breeze, others as safe
            if len(possible_pits_here) == 1:
                confirmed_pit = list(possible_pits_here)[0]
                # Other adjacent rooms to this breeze are safe
                for room in adjacent_to_breeze - {confirmed_pit}:
                    if room not in observations:
                        safe_rooms.add(room)
    
    # Same pit idnetifyifaciotn for wumpus locations
    stench_locations = [loc for loc, o in observations.items() if o[STENCH] == "Stench"]
    if stench_locations and wumpus_alive:
        all_rooms = set((i, j) for i in range(1, 5) for j in range(1, 5))
        consistent_wumpus_locs = set()
        
        for candidate in all_rooms - set(observations.keys()):
            is_consistent = True
            for stench_loc in stench_locations:
                if candidate not in adjacent_rooms(stench_loc):
                    is_consistent = False
                    break
            
            no_stench_locations = [loc for loc, o in observations.items() if o[STENCH] == "None"]
            for no_stench_loc in no_stench_locations:
                if candidate in adjacent_rooms(no_stench_loc):
                    is_consistent = False
                    break
            
            if is_consistent and (not possible_wumpus_loc or candidate in possible_wumpus_loc):
                consistent_wumpus_locs.add(candidate)
        
        if consistent_wumpus_locs:
            possible_wumpus_loc = consistent_wumpus_locs
    
    # Mark rooms as safe if they're not in any danger rooms
    for room in adjacent:
        if room not in possible_wumpus_loc and room not in possible_pit_loc:
            safe_rooms.add(room)
    
    # If definitely found danger rooms, other adjacent rooms safe
    if len(possible_pit_loc) > 0:
        for room in adjacent - possible_pit_loc:
            if room not in possible_wumpus_loc:
                safe_rooms.add(room)
    
    if len(possible_wumpus_loc) > 0 and wumpus_alive:
        for room in adjacent - possible_wumpus_loc:
            if room not in possible_pit_loc:
                safe_rooms.add(room)
    
    # Update possible gold locations
    if obs[GLITTER] == "Glitter":
        possible_gold = {current_loc}
    else:
        possible_gold.discard(current_loc)

def pick_move(world: WumpusWorld) -> str:
    global observations
    global safe_rooms
    global possible_wumpus_loc
    global possible_pit_loc
    global possible_gold
    global wumpus_alive
    global action_queue
    global returning_home

    # Update KB
    update_knowledge(world)
    
    # Escape if spawn next to danger
    if world.player_loc == world.start_loc and len(world.moves) == 0:
        if world.observation[BREEZE] == "Breeze" or world.observation[STENCH] == "Stench":
            print("Danger detected at spawn! Retreating immediately.")
            return "climb"
    
    # Execute queued actions
    if action_queue:
        return action_queue.pop(0)
    
    # Grab gold 
    if world.observation[GLITTER] == "Glitter":
        returning_home = True
        return "grab"
    
    # If gold acquired, go to starting loc
    if world.has_gold or returning_home:
        if world.player_loc != world.start_loc:
            action_queue = list_actions_to_square(world, world.start_loc)
            if action_queue:
                return action_queue.pop(0)
            
    # Confirm at starting loc with gold, skedaddle
    if world.has_gold and world.player_loc == world.start_loc:
        return "climb"
    
    
    # # If wumpus is dead, mark those rooms as safe
    if not wumpus_alive:
        safe_rooms.update(possible_wumpus_loc)
        possible_wumpus_loc.clear()
    
    # Exploration
    unvisited_safe = safe_rooms - set(observations.keys())
    
    if unvisited_safe:
        # Closests unvisited safe room
        target = min(unvisited_safe, key=lambda r: distance(world.player_loc, r))
        action_queue = list_actions_to_square(world, target)
        if action_queue:
            return action_queue.pop(0)
    
    # Last resort go kill wumpus
    if not world.has_gold and wumpus_alive and len(possible_wumpus_loc) == 1:
        wumpus_loc = list(possible_wumpus_loc)[0]
        
        # Check if wumpus is blocking way to rooms behind it
        rooms_behind_wumpus = adjacent_rooms(wumpus_loc) - set(observations.keys()) - possible_pit_loc
        
        if rooms_behind_wumpus:
            # move to adjacent room of wumpus and shoot it
            adjacent_to_wumpus = adjacent_rooms(wumpus_loc) & safe_rooms
            
            if adjacent_to_wumpus:
                # Find closest safe room adjacent to wumpus
                shoot_from = min(adjacent_to_wumpus, key=lambda r: distance(world.player_loc, r))
                
                # path find until we're there
                if world.player_loc != shoot_from:
                    action_queue = list_actions_to_square(world, shoot_from)
                    if action_queue:
                        return action_queue.pop(0)
                
                # Confirm location next to wumpus, kill it
                direction = get_direction_to_neighbor(world.player_loc, wumpus_loc)
                turns = turns_needed(world.facing, direction)
                action_queue = turns + ["shoot"]
                return action_queue.pop(0)
    
    # If no unvisited safe rooms and no gold yet, risk it for the biscuit
    if not world.has_gold:
        # Try adjacent rooms that might be safe (not confirmed hazards)
        adjacent = adjacent_rooms(world.player_loc)
        risky_rooms = adjacent - set(observations.keys()) - possible_pit_loc
        
        if risky_rooms:
            target = choice(list(risky_rooms))
            direction = get_direction_to_neighbor(world.player_loc, target)
            turns = turns_needed(world.facing, direction)
            action_queue = turns + ["forward"]
            return action_queue.pop(0)
    
    # Default: return home if we're stuck (Impossible to find confirm a safe location to move to like if we spawn with diagnol pit)
    if world.player_loc != world.start_loc:
        action_queue = list_actions_to_square(world, world.start_loc)
        if action_queue:
            return action_queue.pop(0)
    
    # Climb out if the dungeon sucks
    return "climb"