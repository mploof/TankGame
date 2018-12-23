import pygame
import copy
import csv

# A list that contains reference GamePiece objects for each piece available in the game
ref_pieces = []

# Create a list containing sets of piece names and their loaded images. Pre-loading the images
# prevents the game from re-opening the images every time and lagging the game
piece_images = []

# The default size of each grid square
grid_size = 0


class Stats:

    def __init__(self, name=None, piece_type=None, health=0, cost=0, ammunition=0, rof=0, speed=0, armor=0,
                 attack_power=0, fuel=0, fuel_consumption=0, power_consumption=0, power_production=0,
                 fixed=False, grid_squares=(0, 0)):

        self.name = name
        self.piece_type = piece_type
        self.health = health
        self.cost = cost
        self.ammunition = ammunition
        self.rof = rof
        self.speed = speed
        self.armor = armor
        self.attack_power = attack_power
        self.fuel = fuel
        self.fuel_consumption = fuel_consumption
        self.power_consumption = power_consumption
        self.power_production = power_production
        self.fixed = fixed
        self.grid_squares = grid_squares


class GamePiece(pygame.sprite.Sprite):

    # The number of pieces currently in play
    count = 0
    pieces = []

    # Returns the image of a piece based upon a request by name
    @staticmethod
    def get_image(name):
        for listing in piece_images:
            if listing[0] is name:
                return listing[1]
        return None

    @staticmethod
    def get_hovered_piece(pos):
        for piece in GamePiece.pieces:
            if piece.is_hovered(pos):
                return piece
        return None

    def __init__(self, stats=None, reference_piece=False):
        # Call the parent class (Sprite) constructor
        super().__init__()

        if reference_piece:
            self.id = -1
        else:
            GamePiece.count += 1
            self.id = GamePiece.count
            # Add this piece to a list containing all pieces in the game
            GamePiece.pieces.append(self)

        # Variables common to all game pieces
        self.stats = copy.copy(stats)

        self.angle = 0

        # If the stats exist, set the sprite image parameters
        if self.stats is not None:
            self.update_sprite()
        # If there aren't any stats, we can't finish the sprite initialization, so just create empty variables for now
        else:
            self.image_size = []
            self.ref_image = None
            self.image = None
            self.rect = None

    def rotate(self, angle):
        self.angle += angle
        self.image = pygame.transform.rotate(pygame.transform.scale(self.ref_image, self.image_size), self.angle)

    # Scale image to x by y pixels
    def scale_image(self, x, y):
        self.image = pygame.transform.scale(self.ref_image, [x, y])

    # Copy the values of another game piece object
    def copy(self, reference):
        # Copy the stats object of the reference rather than assigning all values one-by-one
        self.stats = copy.copy(reference.stats)
        self.update_sprite()

        self.rect.x = reference.rect.x
        self.rect.y = reference.rect.y
        self.angle = 0
        self.rotate(reference.angle)

    def abs_move(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def relative_move(self, x, y):
        self.rect.x += x
        self.rect.y += y

    def update_sprite(self):
        # Values used for sprite generation / manipulation
        self.image_size = [grid_size * self.stats.grid_squares[0],
                           grid_size * self.stats.grid_squares[1]]
        self.ref_image = GamePiece.get_image(self.stats.name)
        self.image = pygame.transform.scale(self.ref_image, self.image_size)
        # Relies on functions from parent (Sprite) class
        self.rect = self.image.get_rect()

    def print(self):
        print("Name:", self.stats.name)
        print("Image:", self.image)
        print("image_size:", self.image_size)
        print("id:", self.id, "\n")

    def is_hovered(self, pos):
        x = pos[0]
        y = pos[1]
        if self.rect.x < x < self.rect.x + self.image_size[0] and \
                self.rect.y < y < self.rect.y + self.image_size[1]:
            return True
        else:
            return False


# Initialize the pieces that will be used in the game from a CSV file
def init(path, default_grid_size=12):
    global grid_size
    grid_size = default_grid_size
    with open(path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        header_row = True
        piece_stats = []
        for row in csv_reader:
            if header_row:
                header_row = False
                continue
            these_stats = Stats(row[0], row[1], int(row[2]), int(row[3]), int(row[4]), int(row[5]), int(row[6]),
                                int(row[7]), int(row[8]), int(row[9]), int(row[10]), int(row[11]), int(row[12]),
                                (False if row[13] is '0' else True), [int(row[14]), int(row[14])])
            piece_stats.append(these_stats)

        for stats in piece_stats:
            # Load the images and convert the alpha layers so they display correctly
            # Don't scale here. That will be done in when creating the pieces so they are the correct grid size
            piece_images.append([stats.name,
                                 pygame.image.load("./assets/alpha/" + stats.piece_type + "_" + stats.name + ".png").
                                convert_alpha()])

            # Create reference pieces to copy from later
            ref_pieces.append(GamePiece(stats, True))


def get_ref_pieces():
    return ref_pieces


# Creates a copy of the named reference piece and returns it
def create_piece(name, is_reference):
    ret = GamePiece(None, is_reference)
    for piece in ref_pieces:
        print(piece.stats.name)
        if piece.stats.name == name:
            ret.copy(piece)
            return ret


def get_grid_size():
    return grid_size
