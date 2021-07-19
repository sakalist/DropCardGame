""" Drop Card Game using pyGame
Author: Tassos Sakalis
Version 1.1
Date:  07/2021
First Release Date: 07/2020

Info:
Suits: H (Hearts), D (Diamonds), S (Spades), C (Clubs)
Numbers: 1 (Ace), 2-10, 11 (Jack), 12 (Queen), 13 (King)
"""
import os
import random
import pygame

# Game Parameters
GAME_WIDTH = 800
GAME_HEIGHT = 730
GAME_SPEED_NORMAL = 10
GAME_SPEED_FAST = 60
BOARD_ZERO_X = 60
BOARD_ZERO_Y = 200
CARD_WIDTH = 85
CARD_HEIGHT = 100
ACTIVE_CARD_START_X = (CARD_WIDTH * 2) + BOARD_ZERO_X  # 230
ACTIVE_CARD_START_Y = 60
CARDS_IN_PACK = 3
STEP = 10
DECK_NUM_START = 1
DECK_NUM_STOP = 13
DECK_SUITS = ['H', 'D', 'C', 'S']


# Game classes
class Card(object):
    def __init__(self, suit, number, image, x=ACTIVE_CARD_START_X, y=ACTIVE_CARD_START_Y):
        self.suit = suit
        self.number = number
        self.image = image
        self.x = x
        self.y = y
        self.board_x = 2
        self.board_y = -1
        self.limit = False
        self.is_at_bottom = False

    def __del__(self):
        """ Display effect image on card removal """
        if not (game_over or activeCard):
            self.image = remove_card_image
            win.blit(self.image, (self.x, self.y))
            pygame.display.update()
            if not clearing_the_stage:
                pygame.time.delay(80)

    def draw(self):
        """ Draw cards on board """
        self.set_card_board_coord()
        win.blit(self.image, (self.x, self.y))

    def set_card_board_coord(self):
        """ Set board array index for cards according with card's position """
        self.board_x = (self.x - BOARD_ZERO_X) // CARD_WIDTH
        self.board_y = (self.y - BOARD_ZERO_Y + CARD_HEIGHT - STEP) // CARD_HEIGHT
        pos_y_limit = (self.y - BOARD_ZERO_Y + CARD_HEIGHT) // CARD_HEIGHT
        if pos_y_limit > self.board_y:
            self.limit = True  # Card is in lower possible place (limit) on current row
        else:
            self.limit = False

    def can_move_down(self, board):
        """ return True if cards can move down else return False """
        # Εάν δεν είναι στο όριο τότε μπορεί να κινηθεί προς τα κάτω
        if not self.limit:
            return True
        else:
            # Εάν είναι στο όριο τότε:
            # α. ελέγχουμε αν έχει φτάσει στον πάτο της πίστας
            if self.board_y == 4:
                self.is_at_bottom = True
                return False
            # β. ελέγχουμε αν έχει απο κάτω άλλο χαρτί
            elif board.grid[self.board_x][self.board_y + 1] is not None:
                return False
            else:
                return True

    def can_move_left(self, board):
        """ return True if cards can move left else return False """
        if self.x > BOARD_ZERO_X:
            if self.board_y == -1 or board.grid[self.board_x - 1][self.board_y] is None:
                return True
        return False

    def can_move_right(self, board):
        """ return True if cards can move right else return False """
        if self.x < 400:  # CARD_WIDTH * 4 + BOARD_ZERO_X
            if self.board_y == -1 or board.grid[self.board_x + 1][self.board_y] is None:
                return True
        return False

    def relocate(self, new_board_x, new_board_y, board):
        """ Relocate cards on board """
        # Remove from old board position
        board.grid[self.board_x][self.board_y] = None
        # set card's new x, y
        self.x = new_board_x * CARD_WIDTH + BOARD_ZERO_X
        self.y = new_board_y * CARD_HEIGHT + BOARD_ZERO_Y
        # set card's new board_x, board_y coordinates
        self.board_x = new_board_x
        self.board_y = new_board_y
        # Place cards in new board position
        board.grid[new_board_x][new_board_y] = self


class Deck(object):
    def __init__(self):
        self.cards = []
        self.populate(DECK_SUITS, DECK_NUM_START, DECK_NUM_STOP)

    def populate(self, suits, num_start, num_stop):
        """ Populate Deck """
        for cardSuit in suits:
            for cardNumber in range(num_start, num_stop + 1):
                card_img = pygame.image.load(os.path.join('data', 'images', cardSuit + '-' + str(cardNumber) + '.png'))
                self.cards.append(Card(cardSuit, cardNumber, card_img))

    def get_one_card(self):
        """ Return a random cards from the deck """
        next_card = random.randrange(0, len(self.cards))
        if len(self.cards):
            return self.cards.pop(next_card)
        else:
            return False


class Pack(object):
    def __init__(self, number_of_cards, deck):
        self.number_of_cards = number_of_cards
        self.cards = []
        self.deck = deck
        self.populate()

    def populate(self):
        for x in range(self.number_of_cards):
            self.cards.append(self.deck.get_one_card())

    def rotate_clockwise(self):
        """ Αλλάζει την ενεργή κάρτα δεξιόστροφα """
        global activeCard
        # Rotate only if cards has cards(s)
        if len(self.cards) > 0:
            # backup activeCard x, y
            last_x = activeCard.x
            last_y = activeCard.y
            # Insert the activeCard at position 0
            self.cards.insert(0, activeCard)
            # set as activeCard the last cards of cards list
            activeCard = self.cards.pop()
            # restore activeCard x, y
            activeCard.x = last_x
            activeCard.y = last_y

    def rotate_counterclockwise(self):
        """ Αλλάζει την ενεργή κάρτα αριστερόστροφα """
        global activeCard
        # Rotate only if cards has cards(s)
        if len(self.cards) > 0:
            # backup activeCard x, y
            last_x = activeCard.x
            last_y = activeCard.y
            # Insert the activeCard at the end
            self.cards.append(activeCard)
            # set as activeCard the first cards of cards list
            activeCard = self.cards.pop(0)
            # restore activeCard x, y
            activeCard.x = last_x
            activeCard.y = last_y

    def draw(self):
        pack_x = 170
        pack_y = 30
        pack_x_step = 30
        for num in range(len(self.cards)):
            self.cards[num].x = pack_x + (num * pack_x_step)
            self.cards[num].y = pack_y
            self.cards[num].draw()


class Reward(object):
    def __init__(self, col, row, value, color=(230, 230, 0)):
        self.col = col
        self.row = row
        self.value = value
        self.color = color
        self.x = self.col * CARD_WIDTH + BOARD_ZERO_X
        self.y = self.row * CARD_HEIGHT + BOARD_ZERO_Y

    def draw(self):
        value_label = rewardFont.render(str(self.value), 1, self.color)
        win.blit(value_label, (self.x, self.y))
        # Move up until top of screen then remove self
        if self.y > -0:
            self.y -= 50
        else:
            rewards.pop(rewards.index(self))


class Board(object):
    def __init__(self):
        self.grid = []
        self.initialize()

    def initialize(self):
        """ Fill board 5x5 array with None """
        for i in range(5):
            self.grid.append([None, None, None, None, None])

    def draw(self):
        for i in range(5):
            for j in range(5):
                if self.grid[i][j] is not None:
                    self.grid[i][j].draw()

    def remove_and_scroll_down(self, col, row, columns):
        # remove cards
        for i in range(columns):
            self.grid[col + i][row] = None
        # scroll down the above cards
        for x in range(col, col + columns):
            for y in range(row - 1, -1, -1):
                if self.grid[x][y]:
                    self.grid[x][y].relocate(x, y + 1, self)

    def check_board(self):
        """ Game Logic. Check board for combinations """
        """ Return True if combination found, card rearranged and need recheck, False otherwise """
        if self.check_5_horizontal():
            soundRemoveCards.play()
            return True
        elif self.check_4_horizontal():
            soundRemoveCards.play()
            return True
        elif self.check_4_vertical():
            soundRemoveCards.play()
            return True
        elif self.check_3_horizontal():
            soundRemoveCards.play()
            return True
        elif self.check_3_vertical():
            soundRemoveCards.play()
            return True
        return False

    def check_5_horizontal(self):
        """ Check 5 same suit horizontal """
        global score
        for row in range(5):
            if self.grid[0][row] and self.grid[1][row] and self.grid[2][row] and self.grid[3][row] and \
                    self.grid[4][row]:
                if self.is_sequence(0, row, 5, True) and self.is_same_suit_horizontal(0, row, 5):
                    # Found 5 sequence and same suit horizontal
                    # Check for intersect on center column
                    # row must be < 3 so that a 3 card column may exist
                    if row < 3 and (self.is_same_number_vertical(2, row, 3) or
                                    self.is_same_suit_vertical(2, row, 3) or
                                    self.is_sequence(2, row, 3, True)):
                        # Intersect Found
                        points = 6000
                        # remove intersected column
                        for i in range(1, 3):
                            self.grid[2][row + i] = None
                    else:
                        points = 2000
                    score += points
                    rewards.append(Reward(0, row, points))
                    self.remove_and_scroll_down(0, row, 5)
                    return True
                elif self.is_sequence(0, row, 5, True):
                    # Found 5 sequence horizontal
                    # Check for intersect on center column
                    if row < 3 and (self.is_same_number_vertical(2, row, 3)
                                    or self.is_same_suit_vertical(2, row, 3)
                                    or self.is_sequence(2, row, 3, False)):
                        # Intersect Found
                        points = 2000
                        # remove intersected column
                        for i in range(1, 3):
                            self.grid[2][row + i] = None
                    else:
                        points = 500
                    score += points
                    rewards.append(Reward(0, row, points))
                    self.remove_and_scroll_down(0, row, 5)
                    return True
                elif self.is_same_suit_horizontal(0, row, 5):
                    # Found 5 same suit horizontal
                    # Check for intersect on center column
                    if row < 3 and (self.is_same_number_vertical(2, row, 3)
                                    or self.is_same_suit_vertical(2, row, 3)
                                    or self.is_sequence(2, row, 3, False)):
                        # Intersect Found
                        points = 1000
                        # remove intersected column 2 cards. The 3rd will be removed with the intersected line)
                        for i in range(1, 3):
                            self.grid[2][row + i] = None
                    else:
                        points = 300
                    score += points
                    rewards.append(Reward(0, row, points))
                    self.remove_and_scroll_down(0, row, 5)
                    return True
        return False

    def check_4_horizontal(self):
        """ Check 4 same suit horizontal """
        global score
        for col in range(2):
            for row in range(5):
                if self.grid[col][row] and self.grid[col + 1][row] and self.grid[col + 2][row] and \
                        self.grid[col + 3][row]:
                    if self.is_sequence(col, row, 4, True) and self.is_same_suit_horizontal(col, row, 4):
                        # Found 4 sequence and same suit horizontal
                        # Check for intersect in middle columns
                        # row must be < 3 so that a 3 card column may exist
                        if row < 3 and (self.is_same_number_vertical(col + 1, row, 3) or
                                        self.is_same_suit_vertical(col + 1, row, 3) or
                                        self.is_sequence(col + 1, row, 3, False)):
                            # Intersect Found on left side of four
                            points = 3000
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col + 1][row + i] = None
                        elif row < 3 and (self.is_same_number_vertical(col + 2, row, 3) or
                                          self.is_same_suit_vertical(col + 2, row, 3) or
                                          self.is_sequence(col + 2, row, 3, False)):
                            # Intersect Found on right side of four
                            points = 3000
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col + 2][row + i] = None
                        else:
                            points = 1000
                        score += points
                        rewards.append(Reward(col, row, points))
                        self.remove_and_scroll_down(col, row, 4)
                        return True
                    elif self.is_same_number_horizontal(col, row, 4):
                        # Found 4 same number horizontal
                        # Check for intersect in middle columns
                        if row < 3 and (self.is_same_number_vertical(col + 1, row, 3) or
                                        self.is_same_suit_vertical(col + 1, row, 3) or
                                        self.is_sequence(col + 1, row, 3, False)):
                            # Intersect Found on left side of four
                            points = 1500
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col + 1][row + i] = None
                        elif row < 3 and (self.is_same_number_vertical(col + 2, row, 3) or
                                          self.is_same_suit_vertical(col + 2, row, 3) or
                                          self.is_sequence(col + 2, row, 3, False)):
                            # Intersect Found on right side of four
                            points = 1500
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col + 2][row + i] = None
                        else:
                            points = 500
                        score += points
                        rewards.append(Reward(col, row, points))
                        self.remove_and_scroll_down(col, row, 4)
                        return True
                    elif self.is_sequence(col, row, 4, True):
                        # Found 4 sequence horizontal
                        # Check for intersect in middle columns
                        if row < 3 and (self.is_same_number_vertical(col + 1, row, 3) or
                                        self.is_same_suit_vertical(col + 1, row, 3) or
                                        self.is_sequence(col + 1, row, 3, False)):
                            # Intersect Found on left side of four
                            points = 1000
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col + 1][row + i] = None
                        elif row < 3 and (self.is_same_number_vertical(col + 2, row, 3) or
                                          self.is_same_suit_vertical(col + 2, row, 3) or
                                          self.is_sequence(col + 2, row, 3, False)):
                            # Intersect Found on right side of four
                            points = 1000
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col + 2][row + i] = None
                        else:
                            points = 300
                        score += points
                        rewards.append(Reward(col, row, points))
                        self.remove_and_scroll_down(col, row, 4)
                        return True
                    elif self.is_same_suit_horizontal(col, row, 4):
                        # Found 4 same suit horizontal
                        # Check for intersect in middle columns
                        if row < 3 and (self.is_same_number_vertical(col + 1, row, 3) or
                                        self.is_same_suit_vertical(col + 1, row, 3) or
                                        self.is_sequence(col + 1, row, 3, False)):
                            # Intersect Found on left side of four
                            points = 500
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col + 1][row + i] = None
                        elif row < 3 and (self.is_same_number_vertical(col + 2, row, 3) or
                                          self.is_same_suit_vertical(col + 2, row, 3) or
                                          self.is_sequence(col + 2, row, 3, False)):
                            # Intersect Found on right side of four
                            points = 500
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col + 2][row + i] = None
                        else:
                            points = 100
                        score += points
                        rewards.append(Reward(col, row, points))
                        self.remove_and_scroll_down(col, row, 4)
                        return True
        return False

    def check_4_vertical(self):
        """ Check 4 same suit vertical """
        global score
        for col in range(5):
            for row in range(2):
                if self.grid[col][row] and self.grid[col][row + 1] and self.grid[col][row + 2] and \
                        self.grid[col][row + 3]:
                    if self.is_sequence(col, row, 4, False) and self.is_same_suit_vertical(col, row, 4):
                        # Found 4 sequence and same suit vertical
                        points = 1000
                        score += points
                        rewards.append(Reward(col, row, points))
                        # remove cards
                        for i in range(0, 4):
                            self.grid[col][row + i] = None
                        return True
                    elif self.is_same_number_vertical(col, row, 4):
                        # Found 4 same suit vertical
                        points = 500
                        score += points
                        rewards.append(Reward(col, row, points))
                        # remove cards
                        for i in range(0, 4):
                            self.grid[col][row + i] = None
                        return True
                    elif self.is_sequence(col, row, 4, False):
                        # Found 4 sequence vertical
                        points = 300
                        score += points
                        rewards.append(Reward(col, row, points))
                        # remove cards
                        for i in range(0, 4):
                            self.grid[col][row + i] = None
                        return True
                    elif self.is_same_suit_vertical(col, row, 4):
                        # Found 4 same suit vertical
                        points = 100
                        score += points
                        rewards.append(Reward(col, row, points))
                        # remove cards
                        for i in range(0, 4):
                            self.grid[col][row + i] = None
                        return True
        return False

    def check_3_horizontal(self):
        """ Check 3 same suit horizontal """
        global score
        for col in range(3):
            for row in range(5):
                if self.grid[col][row] and self.grid[col + 1][row] and self.grid[col + 2][row]:
                    # Found 3 horizontal cards
                    if self.is_sequence(col, row, 3, True) and self.is_same_suit_horizontal(col, row, 3):
                        # Found 3 sequence and same suit horizontal
                        # Check for intersect in either of 3 columns
                        # row must be < 3 so that a 3 card column may exist
                        if row < 3 and (self.is_same_number_vertical(col, row, 3) or
                                        self.is_same_suit_vertical(col, row, 3) or
                                        self.is_sequence(col, row, 3, False)):
                            # Intersect Found on left side of four
                            points = 1500
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col][row + i] = None
                        elif row < 3 and (self.is_same_number_vertical(col + 1, row, 3) or
                                          self.is_same_suit_vertical(col + 1, row, 3) or
                                          self.is_sequence(col + 1, row, 3, False)):
                            # Intersect Found on right side of four
                            points = 1500
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col + 1][row + i] = None
                        elif row < 3 and (self.is_same_number_vertical(col + 2, row, 3) or
                                          self.is_same_suit_vertical(col + 2, row, 3) or
                                          self.is_sequence(col + 2, row, 3, False)):
                            # Intersect Found on right side of four
                            points = 1500
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col + 2][row + i] = None
                        else:
                            points = 500
                        score += points
                        rewards.append(Reward(col, row, points))
                        self.remove_and_scroll_down(col, row, 3)
                        return True
                    elif self.is_same_number_horizontal(col, row, 3):
                        # Found 3 same number horizontal
                        # Check for intersect in either of 3 columns
                        if row < 3 and (self.is_same_number_vertical(col, row, 3) or
                                        self.is_same_suit_vertical(col, row, 3) or
                                        self.is_sequence(col, row, 3, False)):
                            # Intersect Found on left side of four
                            points = 1000
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col][row + i] = None
                        elif row < 3 and (self.is_same_number_vertical(col + 1, row, 3) or
                                          self.is_same_suit_vertical(col + 1, row, 3) or
                                          self.is_sequence(col + 1, row, 3, False)):
                            # Intersect Found on right side of four
                            points = 1000
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col + 1][row + i] = None
                        elif row < 3 and (self.is_same_number_vertical(col + 2, row, 3) or
                                          self.is_same_suit_vertical(col + 2, row, 3) or
                                          self.is_sequence(col + 2, row, 3, False)):
                            # Intersect Found on right side of four
                            points = 1000
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col + 2][row + i] = None
                        else:
                            points = 300
                        score += points
                        rewards.append(Reward(col, row, points))
                        self.remove_and_scroll_down(col, row, 3)
                        return True
                    elif self.is_sequence(col, row, 3, True):
                        # Found 3 on sequence
                        # Check for intersect in either of 3 columns
                        # row must be < 3 so that a 3 card column may exist
                        if row < 3 and (self.is_same_number_vertical(col, row, 3) or
                                        self.is_same_suit_vertical(col, row, 3) or
                                        self.is_sequence(col, row, 3, False)):
                            # Intersect Found on left side of four
                            points = 600
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col][row + i] = None
                        elif row < 3 and (self.is_same_number_vertical(col + 1, row, 3) or
                                          self.is_same_suit_vertical(col + 1, row, 3) or
                                          self.is_sequence(col + 1, row, 3, False)):
                            # Intersect Found on right side of four
                            points = 600
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col + 1][row + i] = None
                        elif row < 3 and (self.is_same_number_vertical(col + 2, row, 3) or
                                          self.is_same_suit_vertical(col + 2, row, 3) or
                                          self.is_sequence(col + 2, row, 3, False)):
                            # Intersect Found on right side of four
                            points = 600
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col + 2][row + i] = None
                        else:
                            points = 100
                        score += points
                        rewards.append(Reward(col, row, points))
                        self.remove_and_scroll_down(col, row, 3)
                        return True
                    elif self.is_same_suit_horizontal(col, row, 3):
                        # Found 3 same suit horizontal
                        # Check for intersect in either of 3 columns
                        if row < 3 and (self.is_same_number_vertical(col, row, 3) or
                                        self.is_same_suit_vertical(col, row, 3) or
                                        self.is_sequence(col, row, 3, False)):
                            # Intersect Found on left side of four
                            points = 500
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col][row + i] = None
                        elif row < 3 and (self.is_same_number_vertical(col + 1, row, 3) or
                                          self.is_same_suit_vertical(col + 1, row, 3) or
                                          self.is_sequence(col + 1, row, 3, False)):
                            # Intersect Found on right side of four
                            points = 500
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col + 1][row + i] = None
                        elif row < 3 and (self.is_same_number_vertical(col + 2, row, 3) or
                                          self.is_same_suit_vertical(col + 2, row, 3) or
                                          self.is_sequence(col + 2, row, 3, False)):
                            # Intersect Found on right side of four
                            points = 500
                            # remove intersected column
                            for i in range(1, 3):
                                self.grid[col + 2][row + i] = None
                        else:
                            points = 10
                        score += points
                        rewards.append(Reward(col, row, points))
                        self.remove_and_scroll_down(col, row, 3)
                        return True
        return False

    def check_3_vertical(self):
        """ Check 3 same suit vertical """
        global score
        for col in range(5):
            for row in range(3):
                if self.grid[col][row] and self.grid[col][row + 1] and self.grid[col][row + 2]:
                    if self.is_sequence(col, row, 3, False) and self.is_same_suit_vertical(col, row, 3):
                        # Found 3 sequence and same suit vertical
                        points = 500
                        score += points
                        rewards.append(Reward(col, row, points))
                        # remove cards
                        for i in range(0, 3):
                            self.grid[col][row + i] = None
                        return True
                    elif self.is_same_number_vertical(col, row, 3):
                        # Found 3 same number vertical
                        points = 300
                        score += points
                        rewards.append(Reward(col, row, points))
                        # remove cards
                        for i in range(0, 3):
                            self.grid[col][row + i] = None
                        return True
                    elif self.is_sequence(col, row, 3, False):
                        # Found sequence of 3 vertical
                        points = 100
                        score += points
                        rewards.append(Reward(col, row, points))
                        # remove cards
                        for i in range(0, 3):
                            self.grid[col][row + i] = None
                        return True
                    elif self.is_same_suit_vertical(col, row, 3):
                        # Found 3 same suit vertical
                        points = 10
                        score += points
                        rewards.append(Reward(col, row, points))
                        # remove cards
                        for i in range(0, 3):
                            self.grid[col][row + i] = None
                        return True
        return False

    def is_same_suit_vertical(self, col, start_row, number_of_cards):
        """ Return True if same suit vertical """
        suit = self.grid[col][start_row].suit
        for i in range(start_row + 1, start_row + number_of_cards):
            if self.grid[col][i].suit != suit:
                return False
        return True

    def is_same_number_vertical(self, col, start_row, number_of_cards):
        """ Return True if same number vertical """
        number = self.grid[col][start_row].number
        for i in range(start_row + 1, start_row + number_of_cards):
            if self.grid[col][i].number != number:
                return False
        return True

    def is_same_suit_horizontal(self, start_col, row, number_of_cards):
        """ Return True if same suit horizontal """
        suit = self.grid[start_col][row].suit
        for i in range(start_col + 1, start_col + number_of_cards):
            if self.grid[i][row].suit != suit:
                return False
        return True

    def is_same_number_horizontal(self, start_col, row, number_of_cards):
        """ Return True if same number horizontal """
        number = self.grid[start_col][row].number
        for i in range(start_col + 1, start_col + number_of_cards):
            if self.grid[i][row].number != number:
                return False
        return True

    def is_sequence(self, col, row, number_of_cards, is_horizontal):
        """ Returns True if cards in horizontal or vertical sequence """
        seq = []
        # Fill the list seq with card numbers
        if is_horizontal:
            # Put horizontal cards into list
            for i in range(col, col + number_of_cards):
                seq.append(self.grid[i][row].number)
        else:
            # Put vertical cards into list
            for i in range(row, row + number_of_cards):
                seq.append(self.grid[col][i].number)
        # Check for sequence (normal: 2,3,4 or 4,3,2 - rotated: Q,K,A,2 or 3,2,A,K etc)
        ascent = all((seq[i] == seq[i + 1] - 1 or seq[i] == seq[i + 1] + 12) for i in range(len(seq) - 1))
        descent = all((seq[i] == seq[i + 1] + 1 or seq[i] == seq[i + 1] - 12) for i in range(len(seq) - 1))
        return ascent or descent


# Game functions (Stages)
def start_stage():
    """ The Introduction Stage """
    global score, stage, level, gameSpeed

    # Start Screen loop
    running = True
    while running:
        # Check for events
        for event in pygame.event.get():
            # Check for QUIT event
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    # Start New Game
                    score = 0
                    stage = level = 1
                    gameSpeed = GAME_SPEED_NORMAL
                    pygame.mixer.music.play(-1)  # Start background music. -1 means infinite loop
                    start_next_stage = True
                    while start_next_stage:
                        # each iteration is a new stage
                        intro_stage()
                        start_next_stage = game_stage()
                    pygame.mixer.music.stop()  # Stop background music
        win.blit(startBg, (0, 0))
        pygame.display.update()


def game_stage():
    """ The main Game Stage """
    global score, stage, level, gameSpeed, game_over, clearing_the_stage, activeCard
    # Initialize game control variables
    game_over = False
    game_over_played = False
    clearing_the_stage = False
    cards_to_clear = []

    # Initialize Game Board 5x5 table
    board = Board()

    # Create Game Deck
    deck = Deck()

    # Create first 3 visible card pack
    pack = Pack(CARDS_IN_PACK, deck)

    # Create first activeCard
    activeCard = deck.get_one_card()

    # Game loop
    running = True
    while running:
        # Check for events
        for event in pygame.event.get():
            # Check for QUIT event
            if event.type == pygame.QUIT:
                game_over = True
                running = False
            # Check if key is Down (once)
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_LEFT and activeCard and activeCard.can_move_left(board):
                    activeCard.x -= CARD_WIDTH
                if event.key == pygame.K_RIGHT and activeCard and activeCard.can_move_right(board):
                    activeCard.x += CARD_WIDTH
                if event.key == pygame.K_LALT:
                    pack.rotate_counterclockwise()
                if event.key == pygame.K_LCTRL:
                    pack.rotate_clockwise()
                if event.key == pygame.K_p:  # Trigger paused
                    pause_stage()
                if event.key == pygame.K_ESCAPE:
                    game_over = True
                    running = False

        # Check keys pressed (continuously)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            clock.tick(GAME_SPEED_FAST)
        else:
            clock.tick(gameSpeed)

        win.blit(gameBg, (0, 0))
        # Draw Cards Left
        win.blit(cardsLeftLabel, (600, 60))
        cards_left_render = font.render(str(len(deck.cards) + len(pack.cards)), 1, (255, 255, 255))
        win.blit(cards_left_render, (660, 92))
        # Draw Stage
        win.blit(stageLabel, (635, 190))
        stage_render = font.render(str(stage), 1, (255, 255, 255))
        win.blit(stage_render, (665, 218))
        # Draw Level
        win.blit(levelLabel, (635, 250))
        level_render = font.render(str(level), 1, (255, 255, 255))
        win.blit(level_render, (665, 275))
        # Draw Score
        win.blit(scoreLabel, (630, 392))
        score_render = font.render(str(score), 1, (255, 255, 255))
        win.blit(score_render, (650, 422))

        # Draw Card Pack
        pack.draw()

        # Draw Cards on board
        board.draw()

        # Draw activeCard if exist
        if activeCard:
            activeCard.draw()

            if activeCard.can_move_down(board):
                activeCard.y += STEP
            else:
                # Check if active cards is not on top of 3 cards pack
                if activeCard.board_y > -1:
                    # activeCard is not outside of board
                    # Place activeCard in current Board location
                    board.grid[activeCard.board_x][activeCard.board_y] = activeCard
                    soundPlaceActive.play()
                    activeCard = None
                    # Check board for combinations until all of them are scored
                    need_recheck = board.check_board()
                    while need_recheck:
                        need_recheck = board.check_board()
                    # Make next active card from pack if pack has card(s)
                    if len(pack.cards):
                        activeCard = pack.cards.pop()
                        activeCard.x = ACTIVE_CARD_START_X
                        activeCard.y = ACTIVE_CARD_START_Y
                        # Fill pack with deck card if deck has card(s)
                        if len(deck.cards):
                            pack.cards.insert(0, deck.get_one_card())
                    else:
                        # Out of cards - Stage Over
                        # Put all remaining cards in the list: cards_to_clear
                        # Check empty stage to give bonus
                        # and activate flag: clearing_the_stage
                        for i in range(5):
                            for j in range(5):
                                if board.grid[i][j]:
                                    cards_to_clear.append(board.grid[i][j])
                        if not len(cards_to_clear):
                            # Stage dont have remaining cards, give bonus
                            points = 1000 + ((level - 1) * 100)
                            score += points
                            rewards.append(Reward(1, 5, "Bonus: " + str(points), (0, 255, 0)))
                        clearing_the_stage = True
                else:
                    # Card on top of 5 cards pile - GAME OVER
                    game_over = True

        # Draw reward if exist and stop playing until all rewards are gone
        for reward in rewards:
            reward.draw()

        # if game is over display message
        if game_over:
            pygame.mixer.music.stop()
            win.blit(gameOverLabelShadow, (105, 305))
            win.blit(gameOverLabel, (100, 300))
            win.blit(enterOrEscLabelShadow, (163, 403))
            win.blit(enterOrEscLabel, (160, 400))
            if not game_over_played:
                soundGameOver.play()
                game_over_played = True
            if keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER] or keys[pygame.K_ESCAPE]:
                return False  # Return False means Game Over return to start_stage

        # If out of cards then clear stage from remaining cards
        if clearing_the_stage:
            if len(cards_to_clear):
                card_to_clear = cards_to_clear.pop()
                points = -100 * level
                score += points
                rewards.append(Reward(card_to_clear.board_x, card_to_clear.board_y, points, (255, 0, 0)))
                board.grid[card_to_clear.board_x][card_to_clear.board_y] = None
                soundMinusCards.play()
                pygame.time.delay(100)
            else:
                # Stage cleared
                clearing_the_stage = False
                if score > 0:
                    stage += 1
                    level = stage // 3 + 1  # get level every 3 stages
                    if stage % 10:
                        gameSpeed += 2  # Increase game speed +2 on every stage
                    else:
                        gameSpeed = GAME_SPEED_NORMAL  # every 10 stages reset speed
                    return True  # return True means goto Next level
                else:
                    game_over = True

        pygame.display.update()
    return False  # Return False means Game Over return to start_stage


def pause_stage():
    """ The stage displayed when a user press the P (pause) key"""
    pygame.mixer.music.pause()
    game_paused = True
    while game_paused:
        for event in pygame.event.get():
            # Check for QUIT event
            if event.type == pygame.QUIT:
                game_paused = False
            # Check if key is Down (once)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    game_paused = False
        win.blit(gameBg, (0, 0))
        pause_render = font.render("Press P to resume", 1, (255, 255, 255))
        win.blit(pause_render, (170, 80))
        pause_label = rewardFont.render('PAUSED', 1, (255, 255, 255))
        pause_label_shadow = rewardFont.render('PAUSED', 1, (0, 0, 0))
        win.blit(pause_label_shadow, (160, 400))
        win.blit(pause_label, (155, 395))

        pygame.display.update()
    pygame.mixer.music.unpause()


def intro_stage():
    """ Stage that shows the stage number. Called before each stage begins """
    # If exist clear all rewards
    while rewards:
        win.blit(intro_stage_image, (0, 0))
        for reward in rewards:
            reward.draw()
        clock.tick(GAME_SPEED_NORMAL)
        pygame.display.update()
    # Display stage number
    win.blit(intro_stage_image, (0, 0))
    stage_label = rewardFont.render('STAGE ' + str(stage), 1, (255, 255, 255))
    stage_label_shadow = rewardFont.render('STAGE ' + str(stage), 1, (0, 0, 0))
    win.blit(stage_label_shadow, (150, 400))
    win.blit(stage_label, (145, 395))
    pygame.display.update()
    pygame.time.delay(1500)


# Pre initialize sound to avoid delay
pygame.mixer.pre_init(44100, -16, 1, 512)
# Initialize pyGame
pygame.init()
clock = pygame.time.Clock()

# Center Game Window in screen
# https://www.pygame.org/wiki/SettingWindowPosition
screenWidth = pygame.display.Info().current_w
screenHeight = pygame.display.Info().current_h
winX = (screenWidth - GAME_WIDTH) // 2
winY = (screenHeight - GAME_HEIGHT) // 2
os.environ['SDL_VIDEO_WINDOW_POS'] = '%d, %d' % (winX, winY)

# Load icons, images and fonts
icon = pygame.image.load(os.path.join('data', 'images', 'deck-icon.png'))
startBg = pygame.image.load(os.path.join('data', 'images', 'start-screen.png'))
gameBg = pygame.image.load(os.path.join('data', 'images', 'board.png'))
intro_stage_image = pygame.image.load(os.path.join('data', 'images', 'tiles.png'))
remove_card_image = pygame.image.load(os.path.join('data', 'images', 'remove-card.png'))
font = pygame.font.Font(os.path.join('data', 'fonts', 'postnobillscolombo-semibold.ttf'), 32)
rewardFont = pygame.font.Font(os.path.join('data', 'fonts', 'postnobillscolombo-bold.ttf'), 72)
cardsLeftLabel = font.render('CARDS LEFT', 1, (255, 255, 255))
stageLabel = font.render('STAGE', 1, (255, 255, 255))
levelLabel = font.render('LEVEL', 1, (255, 255, 255))
scoreLabel = font.render('SCORE', 1, (255, 255, 255))
gameOverLabel = rewardFont.render('GAME OVER', 1, (255, 255, 0))
gameOverLabelShadow = rewardFont.render('GAME OVER', 1, (0, 0, 0))
enterOrEscLabel = font.render('Press ENTER or ESC', 1, (255, 255, 255))
enterOrEscLabelShadow = font.render('Press ENTER or ESC', 1, (0, 0, 0))

# Load music and sounds
soundPlaceActive = pygame.mixer.Sound(os.path.join('data', 'sound', 'in-place.wav'))
soundRemoveCards = pygame.mixer.Sound(os.path.join('data', 'sound', 'remove-cards.wav'))
soundMinusCards = pygame.mixer.Sound(os.path.join('data', 'sound', 'pop.wav'))
soundGameOver = pygame.mixer.Sound(os.path.join('data', 'sound', 'game-over.wav'))
pygame.mixer.music.load(os.path.join('data', 'sound', 'music.wav'))

# Screen properties
win = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
pygame.display.set_caption('Drop Card Game')
pygame.display.set_icon(icon)

# Initialize variables to be global
activeCard = None
rewards = []
score = 0
stage = level = 1
gameSpeed = GAME_SPEED_NORMAL
game_over = clearing_the_stage = False

if __name__ == '__main__':
    # Start Game
    start_stage()

    pygame.quit()
