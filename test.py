# -*- coding: utf-8 -*-
from __future__ import division
import libtcodpy as libtcod
import math
import textwrap
from unidecode import unidecode
import pnpoly


# actual size of the window
SCREEN_WIDTH = 160
SCREEN_HEIGHT = 100

GLOBALMAP_WIDTH = 600
GLOBALMAP_HEIGHT = 300

# size of the map
MAP_WIDTH = 161
MAP_HEIGHT = 91

MAP_WIDTH2 = 80
MAP_HEIGHT2 = 45


currentCell = dict(x =0,y=0)



# sizes and coordinates relevant for the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
INVENTORY_WIDTH = 50



# spell values
HEAL_AMOUNT = 4

FOV_ALGO = 0  # default FOV algorithm
FOV_LIGHT_WALLS = True  # light walls or not
TORCH_RADIUS = 10

LIMIT_FPS = 40  # 20 frames-per-second maximum

color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)




class Zone:
    def __init__(self, id, name, tiles, desc, coords):
        self.tiles = tiles
        self.desc = desc
        self.name = name
        self.id = id
        self.coords = coords
        self.preppedCoords=numpy.array([])

class Tile:
    # a tile of the map and its properties
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked

        # all tiles start unexplored
        self.explored = False

        # by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight



class Object:
    # this is a generic object: the player, a monster, an item, the stairs...
    # it's always represented by a character on screen.
    def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
        self.fighter = fighter
        if self.fighter:  # let the fighter component know who owns it
            self.fighter.owner = self

        self.ai = ai
        if self.ai:  # let the AI component know who owns it
            self.ai.owner = self

        self.item = item
        if self.item:  # let the Item component know who owns it
            self.item.owner = self

    def move(self, dx, dy):
        # move by the given amount, if the destination is not blocked
        #if not is_blocked(MAP_WIDTH//2 + dx, MAP_HEIGHT//2 + dy):
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def move_towards(self, target_x, target_y):
        # vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # normalize it to length 1 (preserving direction), then round it and
        # convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def distance_to(self, other):
        # return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def send_to_back(self):
        # make this object be drawn first, so all others appear above it if they're in the same tile.
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def draw(self):

        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, MAP_WIDTH//2, MAP_HEIGHT//2, self.char, libtcod.BKGND_NONE)

    def clear(self):
        # erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)


class Fighter:
    # combat-related properties and methods (monster, player, NPC).
    def __init__(self, hp, defense, power, death_function=None):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.death_function = death_function

    def attack(self, target):
        # a simple formula for attack damage
        damage = self.power - target.fighter.defense

        if damage > 0:
            # make the target take some damage
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
            target.fighter.take_damage(damage)
        else:
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')

    def take_damage(self, damage):
        # apply damage if possible
        if damage > 0:
            self.hp -= damage

            # check for death. if there's a death function, call it
            if self.hp <= 0:
                function = self.death_function
                if function is not None:
                    function(self.owner)

    def heal(self, amount):
        # heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp





def is_blocked(x, y):
    # first test the map tile
    if traversalMap[x,y]==1:
        return True

    return False



def place_objects(room):

    # choose random number of items
    num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)

    for i in range(num_items):
        # choose random spot for this item
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        # only place it if the tile is not blocked
        if not is_blocked(x, y):
            # create a healing potion
            item_component = Item(use_function=cast_heal)

            item = Object(x, y, '!', 'healing potion', libtcod.violet, item=item_component)

            objects.append(item)
            item.send_to_back()  # items appear below other objects


def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    # render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    # render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    # now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    # finally, some centered text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
                             name + ': ' + str(value) + '/' + str(maximum))


def get_names_under_mouse():
    global mouse

    # return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    # create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj.name for obj in objects
             if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y)]

    names = ', '.join(names)  # join the names, separated by commas
    return names.capitalize()


def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute
    global pix

    #libtcod.image_blit(pix, con, 0, 0, libtcod.BKGND_SET, 0.5, 0.5, 0)
    #libtcod.image_blit_2x(pix, con, 0, 0, 0, 0, -1, -1)



    # draw all objects in the list, except the player. we want it to
    # always appear over all other objects! so it's drawn later.
    #for object in objects:
    #    if object != player:
    #        object.draw()



    #for x1 in range(-MAP_WIDTH2, MAP_WIDTH2):
    #    for y1 in range(-MAP_HEIGHT2, MAP_HEIGHT2):
    #        if is_blocked(x1 + player.x, y1 + player.y):
    #            libtcod.console_put_char(con, MAP_WIDTH2 + x1, MAP_HEIGHT2 + y1, '#', libtcod.BKGND_NONE)
    #        else:
    #            libtcod.console_put_char(con, MAP_WIDTH2 + x1, MAP_HEIGHT2 + y1, ' ', libtcod.BKGND_NONE)

    player.draw()




    # blit the contents of "con" to the root console
    libtcod.console_blit(con, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0, 0)

    # prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    libtcod.console_print(panel,0,0,str(currentCell['x'])+','+str(currentCell['y']))

    x = currentCell['x'] / GLOBALMAP_WIDTH
    y = currentCell['y'] / GLOBALMAP_HEIGHT

    for id,zone in zones.iteritems():
        vx = numpy.array(zone.preppedCoords[:,0])
        vy = numpy.array(zone.preppedCoords[:,1])
        if pnpoly.pnpoly2(x, y, vx, vy):
            libtcod.console_print(panel, 10, 0, unidecode(zone.name))
            message(zone.desc)

    currentCellDesc = [];
    for id, zone in zones.iteritems():
        if (currentCell['x'],currentCell['y']) in zone.tiles:
            currentCellDesc.append(zone.desc)






    # print the game messages, one line at a time
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    # show the player's stats
    #render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
    #           libtcod.light_red, libtcod.darker_red)

    # display names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())

    # blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)


def message(new_msg, color=libtcod.white):
    # split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        # if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        # add the new line as a tuple, with the text and the color
        game_msgs.append((line, color))


def player_move_or_attack(dx, dy):
    #make_map()
    player.move(dx, dy)





def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    # calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    height = len(options) + header_height

    # create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    # print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    # print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    # blit the contents of "window" to the root console
    x = SCREEN_WIDTH / 2 - width / 2
    y = SCREEN_HEIGHT / 2 - height / 2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    # present the root console to the player and wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    # convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None


def inventory_menu(header):
    # show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in inventory]

    index = menu(header, options, INVENTORY_WIDTH)

    # if an item was chosen, return it
    if index is None or len(inventory) == 0: return None
    return inventory[index].item


def handle_keys():
    global key;
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'  # exit game

    if game_state == 'playing':
        # movement keys
        if key.vk == libtcod.KEY_UP:
            player_move_or_attack(0, -1)

        elif key.vk == libtcod.KEY_DOWN:
            player_move_or_attack(0, 1)

        elif key.vk == libtcod.KEY_LEFT:
            player_move_or_attack(-1, 0)

        elif key.vk == libtcod.KEY_RIGHT:
            player_move_or_attack(1, 0)
        else:
            # test for other keys
            key_char = chr(key.c)

            if key_char == 'g':
                # pick up an item
                for object in objects:  # look for an item in the player's tile
                    if object.x == player.x and object.y == player.y and object.item:
                        object.item.pick_up()
                        break

            if key_char == 'i':
                # show the inventory; if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()

            return 'didnt-take-turn'


def player_death(player):
    # the game ended!
    global game_state
    message('You died!', libtcod.red)
    game_state = 'dead'

    # for added effect, transform the player into a corpse!
    player.char = '%'
    player.color = libtcod.dark_red




def cast_heal():
    # heal the player
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health.', libtcod.red)
        return 'cancelled'

    message('Your wounds start to feel better!', libtcod.light_violet)
    player.fighter.heal(HEAL_AMOUNT)





def isPointInPath(x, y, poly):
    num = len(poly)
    i = 0
    j = num - 1
    c = False
    for i in range(num):
        if ((poly[i][1] > y) != (poly[j][1] > y)) and \
                (x < (poly[j][0] - poly[i][0]) * (y - poly[i][1]) / (poly[j][1] - poly[i][1]) + poly[i][0]):
            c = not c
        j = i
    return c

# Program to flatten an arbitrarily nested list.


def flatten(lis):
    """Given a list, possibly nested to any level, return it flattened."""
    new_lis = []
    for item in lis:
        if isinstance(item, list):
            new_lis.extend(flatten(item))
        else:
            new_lis.append(item)
    return new_lis

def depth(lis,n):
    n = n + 1
    for item in lis:
        if isinstance(item, list):
            depth(item,n)
    return n




#############################################
# Initialization & Main Loop
#############################################

#from osmread import parse_file, Way, Node

#bld_count = 0
#mapNodes=dict()
#for entity in parse_file('map.osm'):
#    if isinstance(entity, Node):
#        mapNodes[entity.id]=entity
#    if isinstance(entity, Way) and 'building' in entity.tags:
#        bld_count += 1
#        for n1 in entity.nodes:
#            #print(mapNodes[n1])

#print("%d highways found" % bld_count)


import json
import numpy

with open('little.geojson','r') as f:
    data = json.load(f)

polys=[]
zones = dict()

xlist = []
ylist=[]

for feature in data['features']:
    #print feature['geometry']['type']
    #print feature['geometry']['coordinates']
    if (('building' in feature['properties']) or ('waterway' in feature['properties'])) and (feature['geometry']['type'] == 'Polygon'):
        zones[feature['id']]=Zone(feature['id'],feature['properties'].get('name'), [], '', feature['geometry']['coordinates'])
        if zones[feature['id']].name==None:
            zones[feature['id']].name=feature['id']
        if (feature['properties'].get('addr:street')) != None:
            zones[feature['id']].desc = zones[feature['id']].desc + unidecode(feature['properties'].get('addr:street'))
        if (feature['properties'].get('addr:housenumber')) != None:
            zones[feature['id']].desc = zones[feature['id']].desc + (feature['properties'].get('addr:housenumber'))
        #if ('multipolygon' == feature['properties'].get('type')):
        coords=flatten(zones[feature['id']].coords)
        i=0
        for pt1c in coords:
            if (i%2)==0:
                xlist.append(pt1c)
            else:
                ylist.append(pt1c)
            i=i+1
        if feature['geometry']['type'] == 'Polygon':
            polys.append(feature['geometry']['coordinates'])
    #if feature['geometry']['type'] == 'MultiPolygon':
    #    poly1.extend(feature['geometry']['coordinates'])

print "Number of zones:" + str(len(data['features']))


#for poly1 in polys:
#    for path1 in poly1:
#        for pt1 in path1:
#            xlist.append(pt1[0])
#            ylist.append(pt1[1])

maxX = max(xlist)
maxY = max(ylist)
minX = min(xlist)
minY = min(ylist)

scaleX = maxX-minX
scaleY = maxY-minY



for id, zone in zones.iteritems():
    poly3 = []
    poly3.append([0, 0])
    for path in zone.coords:
        d1 = depth(path,0)
        for i, pt in enumerate(path):
            path[i][0] = (path[i][0] - minX) / scaleX
            path[i][1] = 1 - (path[i][1] - minY) / scaleY
    poly3.extend(path)
    poly3.append(path[0])
    poly3.append([0, 0])
    zone.preppedCoords = numpy.array(poly3)

batchPolys =polys[:]

#for poly2 in batchPolys:
#    for path2 in poly2:
#        for i, pt2 in enumerate(path2):
#            path2[i][0] = (path2[i][0] - minX) / scaleX
#            path2[i][1] = (path2[i][1] - minY) / scaleY

poly3=[]
poly3.append([0, 0])
for poly2 in batchPolys:
    for path2 in poly2:
        poly3.extend(path2)
        poly3.append(path2[0])
        poly3.append([0,0])
#print maxX,minX,maxY,minY

polyArray=numpy.array(poly3)
#print poly3



#дыра по часовой, граница против
#poly2 = [(1, 1), (1, -1), (-1, -1), (-1, 1), (1, 1), (2, 2), (-2, 2), (-2, -2), (2, -2), (2, 2)]

#poly4 = [(0.5, 0.5), (0.5, -0.5), (-0.5, -0.5), (-0.5, 0.5), (0.5, 0.5), (1, 1), (-1, 1), (-1, -1), (1, -1), (1, 1)]


#print isPointInPath(-1.5, 1.5, polyu2)


#libtcod.line()

libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)

#pix = libtcod.image_new(80,50)
pix = libtcod.image_load("map.png")

# create object representing the player
fighter_component = Fighter(hp=30, defense=2, power=5, death_function=player_death)
player = Object(230, 205, '@', 'player', libtcod.yellow, blocks=False, fighter=fighter_component)

# the list of objects with just the player
objects = [player]

#libtcod.image_blit(pix, con, player.x, player.y, libtcod.BKGND_SET, 0.5, 0.5, 0)

game_state = 'playing'
player_action = None

inventory = []

# create the list of game messages and their colors, starts empty
game_msgs = []

# a warm welcoming message!
#message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', libtcod.red)

mouse = libtcod.Mouse()
key = libtcod.Key()

map=dict();


import time


traversalMap = numpy.array(numpy.zeros((GLOBALMAP_WIDTH,GLOBALMAP_HEIGHT)))


#for zone in zones:


start = time.time()

vx = numpy.array(polyArray[:,0])
vy = numpy.array(polyArray[:,1])

for i in range(0, GLOBALMAP_WIDTH):
    for j in range(0, GLOBALMAP_HEIGHT):
        x = i / GLOBALMAP_WIDTH
        y = j / GLOBALMAP_HEIGHT
        if pnpoly.pnpoly2(x, y, vx, vy):
            traversalMap[i,j]=1

end = time.time()
print(end - start)


while not libtcod.console_is_window_closed():


    # render the screen
    libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

    #libtcod.image_blit(pix, con, player.x, player.y, libtcod.BKGND_SET, 0.5, 0.5, 0)

    mouseStatus = libtcod.mouse_get_status()

    currentCell['x'] = player.x-MAP_WIDTH2 + mouseStatus.cx
    currentCell['y'] = player.y-MAP_HEIGHT2 + mouseStatus.cy

    render_all()

    for i in range(max(player.x-MAP_WIDTH2,0),min(player.x+MAP_WIDTH2,GLOBALMAP_WIDTH)):
        for j in range(max(player.y-MAP_HEIGHT2,0),min(player.y+MAP_HEIGHT2,GLOBALMAP_HEIGHT)):
            if traversalMap[i,j]==1:
                libtcod.console_set_char_background(con, i-player.x+MAP_WIDTH2, j-player.y+MAP_HEIGHT2, libtcod.white)
            else:
                libtcod.console_set_char_background(con, i - player.x + MAP_WIDTH2, j - player.y + MAP_HEIGHT2, libtcod.black)

    libtcod.console_flush()

    # handle keys and exit game if needed
    player_action = handle_keys()
    if player_action == 'exit':
        break
