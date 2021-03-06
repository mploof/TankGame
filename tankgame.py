##########################################
#               Imports                  #
##########################################

import pygame
import gamepieces as gp
import math
import statistics


##########################################
#             Global Vars                #
##########################################
# Initialize Pygame
pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Comic Sans MS', 20)

# Set the height and width of the screen
w = screen_width = 800
h = screen_height = 800
screen = pygame.display.set_mode([screen_width, screen_height])

# Initialize the game pieces
gp.init('./pieces.csv')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

##########################################
#               Classes                  #
##########################################


##########################################
#      Functions and "Static" Vars       #
##########################################

# Draw the unit menu
def draw_menu():
    grid_sz = menu_item_px
    line_px = 2

    # Draw the menu lines
    pygame.draw.line(screen, BLACK, [w - grid_sz, 0], [w - grid_sz, h], line_px)
    for i in range(0, int(h / grid_sz)):
        pygame.draw.line(screen, BLACK, [w - grid_sz, i * grid_sz], [w, i * grid_sz], line_px)


# Return which menu item is selected, if any
# pos -  Mouse position object
def get_menu_selection(pos):
    x = pos[0]
    y = pos[1]
    if w - menu_item_px < x <= w:
        return int(y / menu_item_px)


# Display the info the selected piece
# pos - Mouse position object
# piece - Game piece object
def draw_hover_box(pos, piece):
    x = pos[0] + 25
    y = pos[1] - 25
    points = [(x, y), (x + 250, y), (x + 250, y - 100), (x, y - 100)]
    pygame.draw.lines(screen, BLACK, True, points, 2)
    info = ["Name: " + piece.stats.name,
            "Health: " + str(piece.stats.health),
            "Armor: " + str(piece.stats.armor)]
    i = 0
    for item in info:
        text = font.render(item, False, BLACK)
        screen.blit(text, (x + 10, y - 100 + (i * 25)))
        i += 1


##########################################
#               Main Code                #
##########################################

# Different spite groups used for drawing
menu_sprites = pygame.sprite.Group()   # The sprites to be displayed in the selection menu
player_sprites = pygame.sprite.Group() # Right now, just the currently selected piece
placed_sprites = pygame.sprite.Group() # These are the pieces that have been placed

# Populate the menu sprites with constant sized images
i = 0
menu_item_px = gp.get_grid_size() * 4
for piece in gp.get_ref_pieces():
    this_piece = gp.GamePiece(None, True)
    piece.print()
    this_piece.copy(piece)
    this_piece.scale_image(menu_item_px, menu_item_px)
    this_piece.abs_move(w - menu_item_px, i * menu_item_px + 1)
    menu_sprites.add(this_piece)
    i += 1

# Create an infantry sprite as the initially selected unit
player = gp.create_piece("infantry", True)
player_sprites.add(player)

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()


# -------- Main Loop Vars -----------
was_pressed = False  # Keeps track of the last mouse click state to limit actions to one per click
last_keys = pygame.key.get_pressed()  # A map of all the keys currently pressed
draw_hover = False  # Whether the info box should be drawn over the current piece
magnitude_history = []
pos_history = []
last_pos = None
line_points = []
was_shot = False

# -------- Main Program Loop -----------
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # Clear the screen
    screen.fill(WHITE)

    # Get the current mouse position. This returns the position
    # as a list of two numbers.
    pos = pygame.mouse.get_pos()
    x = pos[0]
    y = pos[1]

    # Check to see if the cursor is over an already placed piece
    current_piece = gp.GamePiece.get_hovered_piece(pos)

    # Determine how fast and where the mouse is moving
    if last_pos is not None:
        # Find the magnitude and add to the history lists
        delta_x = x - last_pos[0]
        delta_y = y - last_pos[1]
        magnitude = math.sqrt(math.pow(delta_x, 2) + math.pow(delta_y, 2))
        magnitude_history.append(magnitude)
        pos_history.append(pos)

        # Once there are enough history points, determine whether the movement was a 'shot'
        if len(magnitude_history) > 4:
            # Drop the oldest item in the history lists
            magnitude_history.pop(0)
            pos_history.pop(0)

            # If there's a high average magnitude register the movement as a shot
            magnitude_ave = statistics.mean(magnitude_history)
            #   But wait until one shot has been completed before registering a new one
            if magnitude_ave > 5 and was_shot is False:
                print("shot from:", pos_history[0])
                # Only shoot if the mouse starting point was over a piece
                if current_piece is not None and current_piece.is_hovered(pos_history[0]) \
                        and current_piece.stats.piece_type is not 'b':
                    line_points.append([[pos_history[0][0], pos_history[0][1]], [x, y]])
                    if len(line_points) > 1:
                        line_points.pop(0)
                    was_shot = True
            elif magnitude_ave < 5:
                was_shot = False

    last_pos = pos

    # Check to see if the mouse is pressed and deal with that
    pressed = pygame.mouse.get_pressed()

    # Display info box on right click when no item is selected
    if pressed[2] is 1 and current_piece is not None and player is None:
        draw_hover = True
    else:
        draw_hover = False

    # Drag selected piece on left click when no piece from the menu is active
    if pressed[0] is 1 and player is None and current_piece is not None:
        current_piece.abs_move(x - current_piece.image_size[0]/2, y - current_piece.image_size[1]/2)

    # On left click, select item from menu or place item on field
    if pressed[0] is 1 and was_pressed is not True:
        was_pressed = True
        pos = pygame.mouse.get_pos()
        menuSelection = get_menu_selection(pos)
        print(menuSelection)
        if menuSelection is not None:
            ref_pieces = gp.get_ref_pieces()
            player = gp.GamePiece(None, True)
            player.copy(ref_pieces[menuSelection])
            player_sprites.empty()
            player_sprites.add(player)
        elif player is not None:
            # place the current unit
            new_unit = gp.GamePiece()
            new_unit.copy(player)
            placed_sprites.add(new_unit)
    elif pressed[0] is 0:
        was_pressed = False

    # Fetch the x and y out of the list,
    # just like we'd fetch letters out of a string.
    # Set the player object to the mouse location
    if player is not None:
        player.rect.x = pos[0] - (player.image.get_rect().size[0] / 2)
        player.rect.y = pos[1] - (player.image.get_rect().size[1] / 2)

    # Draw all the spites
    menu_sprites.draw(screen)
    placed_sprites.draw(screen)
    player_sprites.draw(screen)
    draw_menu()
    for line in line_points:
        pygame.draw.line(screen, BLACK, line[0], line[1])
    if draw_hover:
        draw_hover_box(pos, current_piece)

    # Perform keyboard actions, if necessary
    current_keys = pygame.key.get_pressed()
    #   R - Rotate selected piece clockwise
    if current_keys[pygame.K_r] and last_keys[pygame.K_r] is 0:
        player.rotate(-22.5)
    #   E - Rotate counter clockwise
    if current_keys[pygame.K_e] and last_keys[pygame.K_e] is 0:
        player.rotate(22.5)
    #   Esc - Deselect the currently selected item
    if current_keys[pygame.K_ESCAPE] and last_keys[pygame.K_ESCAPE] is 0:
        player_sprites.empty()
        player = None

    # Used to compare currently pressed keys to the keys pressed during the last loop
    # This allows for executing a command once per key press
    last_keys = current_keys

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # Limit to 60 frames per second
    clock.tick(60)

pygame.quit()
