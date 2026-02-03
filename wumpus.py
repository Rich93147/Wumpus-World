# Author: Gentry Atkinson
# Organization: St. Edwards University

import os
import pygame
from random import randint

IMG = "C:\\Intro to AI\\wumpus\\COSC3340 Playable Wumpus World\\Playable Wumpus World\\imgs"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800

GRID_ROWS = {
  1 : 528,
  2 : 383,
  3 : 240,
  4 : 95
}

GRID_COLS = {
  1 : 118,
  2 : 262,
  3 : 405,
  4 : 548
}


# A class representing the Wumpus World game environment.
class WumpusWorld:
  SIZE = 4
  LEGAL_MOVES = ['forward', 'right', 'left', 'shoot', 'grab', 'climb']

  # Initialize the game environment with random locations for hazards.
  def __init__(self):
    self.player_loc = (1, 1)
    self.__wumpus_loc = (randint(1, self.SIZE), randint(2, self.SIZE))
    self.start_loc = (1, 1)
    self.__gold_loc = (randint(1, self.SIZE), randint(2, self.SIZE))
    self.__pits = self.__generate_pits()
    self.moves = []
    self.observation = ["None"] * 5
    self.facing = (0, 1)  # Initially facing up.
    self.has_gold = False
    self.escape = False
    self.ammo = 1
    self.died = False
    self.action = None
    self.__load_images()
    self.__load_screen()
    self.__init_game()
    self.perceive()

  def __init_game(self):
    # Init Game
    pygame.init()
    self.main_font = pygame.font.Font(os.path.join('C:\\Intro to AI\\wumpus\\COSC3340 Playable Wumpus World\\Playable Wumpus World\\font', 'slkscr.ttf'), 40)
    pygame.display.set_caption('Wumpus World')
    clock = pygame.time.Clock()
    pygame.key.set_repeat()
    self.draw()

  def __load_images(self):
    self.imgs = {
      'world' : pygame.image.load(os.path.join(IMG, 'world.png')),
      'wumpus' : pygame.image.load(os.path.join(IMG, 'wumpus.png')),
      'breeze' : pygame.image.load(os.path.join(IMG, 'breeze.png')),
      'stink' : pygame.image.load(os.path.join(IMG, 'stink.png')),
      'gold' : pygame.image.load(os.path.join(IMG, 'gold.png')),
      'pit' : pygame.image.load(os.path.join(IMG, 'pit.png')),
      'player' : pygame.image.load(os.path.join(IMG, 'player.png')),
      'bubble_e' : pygame.image.load(os.path.join(IMG, 'bubble_empty.png')),
      'bubble_f' : pygame.image.load(os.path.join(IMG, 'bubble_full.png')),
    }

  def __load_screen(self):
       self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) 

  # Randomly generate pit locations, avoiding start and hazard locations.
  def __generate_pits(self):
    pits = []
    for _ in range(randint(1, 4)):
      x, y = randint(1, self.SIZE), randint(1, self.SIZE)
      if (x, y) in [self.start_loc, self.__wumpus_loc, self.__gold_loc]:
        continue
      pits.append((x, y))
    return pits

  # Visualize the current state of the Wumpus World environment.
  def draw(self):

    # Draw grid lines.
    self.__draw_entity("world", (0,0))

    # Draw entities in the environment.
    if self.player_loc:
      self.__draw_entity("player", (GRID_COLS[self.player_loc[0]], GRID_ROWS[self.player_loc[1]]))
    if self.__wumpus_loc:
      self.__draw_entity("wumpus", (GRID_COLS[self.__wumpus_loc[0]], GRID_ROWS[self.__wumpus_loc[1]]))
    if self.__gold_loc:
      self.__draw_entity("gold", (GRID_COLS[self.__gold_loc[0]], GRID_ROWS[self.__gold_loc[1]]))
    for pit in self.__pits:
      self.__draw_entity("pit", (GRID_COLS[pit[0]], GRID_ROWS[pit[1]]))

    # Draw Arrow Indicator
    if self.ammo == 1:
      self.__draw_entity("bubble_f", (240, 715))
    else:
      self.__draw_entity("bubble_e", (240, 715))

    # Draw Gold Indicator
    if self.has_gold:
      self.__draw_entity("bubble_f", (600, 715))
    else:
      self.__draw_entity("bubble_e", (600, 715))

    # Draw Percepts
    p_string = [p for p in self.observation if p != "None"]
    percepts = self.main_font.render(','.join(p_string), 1, (54, 00, 114))
    self.screen.blit(percepts, (300, 649))

    # Draw Action
    if self.action:
      a_string = self.main_font.render(self.action, 1, (54, 00, 114))
      self.screen.blit(a_string, (105, 15))

    pygame.display.update()
    pygame.time.delay(250)

  # Helper function to draw an entity at a specified location.
  def __draw_entity(self, name: str, location: tuple, width=1, height=1):
    if location:
      self.screen.blit(self.imgs[name], location)

  # Update the player's observations based on the current state.
  def perceive(self):
    self.observation = [
        "None", "None", "None", self.observation[3], self.observation[4]
    ]
    if self.player_loc == self.__gold_loc:
      self.observation[2] = "Glitter"
    self.__update_observation_for_hazards()

  def __update_observation_for_hazards(self):
    """Check proximity to Wumpus and pits to update observations."""
    # Check for Wumpus proximity.
    if self.__wumpus_loc and self.__is_adjacent(self.player_loc, self.__wumpus_loc):
      self.observation[0] = "Stench"
    # Check for pit proximity.
    for pit in self.__pits:
      if self.__is_adjacent(self.player_loc, pit):
        self.observation[1] = "Breeze"

  # Determine if two locations are adjacent (excluding diagonal).
  @staticmethod
  def __is_adjacent(loc1, loc2):
    return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1]) == 1

  # Check if the player has died from falling into a pit or encountering the Wumpus.
  def player_dead(self):
    if self.player_loc in self.__pits:
      print("Our hero falls screaming into a bottomless pit.")
      self.died = True
      return True
    if self.player_loc == self.__wumpus_loc:
      print("Our hero is torn to bloody shreds by a ravenous Wumpus.")
      self.died = True
      return True
    return False

  # Perform an action from the set of legal moves and update the game state.
  def act(self, action):
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
    assert action in self.LEGAL_MOVES, "Illegal Action"
    self.action = action
    self.observation[3:] = ["None", "None"]
    self.moves.append(action)
    self.__execute_action(action)
    self.perceive()

  # Internal method to handle the execution of player actions.
  def __execute_action(self, action):
    match action:
      case "forward":
        self.__move_forward()
      case "left":
        self.facing = self.__rotate_left(self.facing)
      case "right":
        self.facing = self.__rotate_right(self.facing)
      case "grab":
        self.__grab_gold()
      case "climb":
        self.__attempt_climb()
      case "shoot":
        self.__shoot_arrow()

  # Attempt to move the player forward based on the current facing direction.
  def __move_forward(self):
    new_x, new_y = (self.player_loc[0] + self.facing[0], self.player_loc[1] + self.facing[1])
    if not (1 <= new_x <= self.SIZE) or not (1 <= new_y <= self.SIZE):
      self.observation[3] = "Bump"
    else:
      self.player_loc = (new_x, new_y)

  # Rotate the player's facing direction to the left.
  @staticmethod
  def __rotate_left(facing):
    return (-facing[1], facing[0])

  # Rotate the player's facing direction to the right.
  @staticmethod
  def __rotate_right(facing):
    return (facing[1], -facing[0])

  # Allow the player to grab gold if it is in the same location.
  def __grab_gold(self):
    if self.player_loc == self.__gold_loc:
      print("Our hero retrieves the glittering gold.")
      self.__gold_loc = None
      self.has_gold = True

  # Check if the player can climb out of the dungeon.
  def __attempt_climb(self):
    if self.player_loc == self.start_loc:
      print("Our hero climbs panting from the wretched dungeon.")
      self.escape = True

  # Handle the shooting of an arrow and its consequences.
  def __shoot_arrow(self):
    if self.ammo > 0:
      self.ammo -= 1
      arrow_loc = (self.player_loc[0] + self.facing[0], self.player_loc[1] + self.facing[1])
      while 1 <= arrow_loc[0] <= self.SIZE and 1 <= arrow_loc[1] <= self.SIZE:
        if arrow_loc == self.__wumpus_loc:
          print("The arrow sinks deeply into the torso of the wailing Wumpus.")
          self.observation[4] = "Scream"
          self.__wumpus_loc = None
          break
        arrow_loc = (arrow_loc[0] + self.facing[0], arrow_loc[1] + self.facing[1])

  # Calculate and return the player's score based on game outcomes.
  def score(self):
    score = -len(self.moves)
    if self.died:
      score -= 1000
    if self.has_gold and self.escape:
      score += 1000
    if self.ammo < 1:
      score -= 10
    return score