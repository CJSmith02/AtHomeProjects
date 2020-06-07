# -*- coding: utf-8 -*-
"""
Created on Mon May 11 21:57:26 2020

@author: Caleb Smith
"""
import euchre_utils
import collections
import random
import re

CARD_VALUES_ORDER = ['9','10','J','Q','K','A']
TRUMP_VALUES_ORDER = ['9','10','Q','K','A','LB','RB']
SUITS = ['clubs','spades','hearts','diamonds']
card = collections.namedtuple("card", ["value", "suit"])

class Player():
    
    """
    a player and their hand of cards instantiated
    """
    def __init__(self, name):
        self.name = name
        self.hand = {s:[] for s in SUITS}
        
    def new_card(self, card):
        self.hand[card.suit].append[card.value]
    
    def remove_card(self, card):
        self.hand[card.suit].remove(card)
        #don't need to sort cause will stay in order
        
    def sort_hand(self, trump):
        """Sorts cards in terms of power, and changes Js to appropriate bowers"""
        left_bower = euchre_utils.get_left_bower(trump)
        #don't sort the trump suit in the for loop cause it could get messed up
        # instead, always sort it after
        for suit in self.hand:
            if suit == left_bower.suit:
                #remove old jack, create left bower
                self.hand[suit].remove(left_bower.value)
                self.hand[trump].append('LB')
                
            if suit != trump: #suit will return the key which can match with trump
                suit.sort(key = CARD_VALUES_ORDER.index)
        
        self.hand[trump].remove('J') #undergo name change
        self.hand[trump].append('RB')
        self.hand[trump].sort(key = TRUMP_VALUES_ORDER)
        
    def print_hand(self):
        for suit in self.hand:
            for card in hand[suit]:
                print("{} of {}".format(card,suit))
    
    def select_card(self, options):
        """ options is the list OR dictionary of lists (hand) from which a valid 
        card can be drawn. This shows the player the options, asks them to type
        the one they want, and tells them they can't have one they can't have"""
        
        answer = input("What card do you want to play?\n")
        value = re.match('9|10|J|Q|K|A|LB|RB', answer.upper())
        suit = re.match('diamonds|hearts|spades|clubs', answer.lower())
        if value and suit: # if they exist
            attempt = card(value.group(0), suit.group(0))
            if type(options) == dict: #a hand
                if value in options[suit]:
                    return attempt
                else:
                    print("Try again. That card is not an option.")
                    self.select_card(options)
            elif type(options) == list:
                if value in options:
                    return attempt
                else:
                    print("Try again. That card is not in your hand.")
                    self.select_card(options)
            else:
                raise TypeError("look in select_card. invalid options input type")
        else:
            print("Try again. You mistyped a card. Make sure to spell out" +
                  "the suit, like 'k clubs'")
            self.select_card(options) # yes it's recursion. it's ok though
        
    
class Deck():
    
    cards = []
    
    def __init__(self):
        #generate the cards
        for suit in SUITS:
            for value in CARD_VALUES_ORDER:
                self.cards.append(card(value,suit))
        # shuffle them
        random.shuffle(self.cards)
    
    def get_card(self):
        return self.cards.pop()
    
    def deal(self, players):
        num_cards_to_deal = iter([3,2,3,2,2,3,2,3])
        for i in range(2): # go around twice
            for player in players: #at each player
                for j in range(next(num_cards_to_deal)): #deal multiple cards
                    player.add_card(self.get_card())
                    

class Team():
    def __init__(self, player1, player2):
        self.members = [player1, player2]
        self.score = 0
        self.tricks_taken_this_round = 0
    
    def reset_tricks_taken(self):
        self.tricks_taken_this_round = 0
            
    
class Table():
    
    """
    the class that governs everything that happens
    """
    def __init__(self, names):
        self.players = [Player(name) for name in names]
        self.teams = [Team(self.players[i], self.players[i+2]) for i in range(
                2)]
        
        self.dealer = self.players[0]
        self.first_player = self.players[1]
        self.deck = Deck()
        
        #round-specific variables that change
        self.round = 1
        self.cards_on_table = []
        self.trump = ''
        self.player_going_alone = None #contains the player object who 'goes alone'
        self.player_that_called_suit = None # player object
               
    def add_card(self, card):
        self.cards_on_table.append(card)
        
    def get_team_player_is_on(self, player):
        for team in self.teams:
            if player in team.members:
                return team
    
    def get_other_team(self, team1):
        for team in self.teams:
            if team != team1: # i thiiiink '==' better than 'is' here
                return team
    
    def clear_cards_on_table(self):
        self.cards_on_table.clear()
        
    def print_cards_on_table(self):
        if self.cards_on_table: # if it's not empty
            for card in self.cards_on_table:
                print("{} of {}".format(card.value, card.suit))
        else:
            print("There are no cards on the table")
        
    def determine_trick_winner(self):
        """
        returns the player object of who played the highest card based on self properties
        """
        winning_card = euchre_utils.get_best_card(self.cards_on_table,
                                                  self.trump)
        winning_card_index = self.cards_on_table.index(winning_card)
        dist_between_player1_and_card1 = self.players.index(self.first_player) #offset because 
        return self.players[(winning_card_index + 
                             dist_between_player1_and_card1) %4]
        
    def compensate_round_winner(self, winning_team):
        """determine which team got how many points, and add them"""
        #which team won
        
        suit_calling_team = self.get_team_player_is_on(
                                            self.player_that_called_suit)
        #how many points should they get
        if winning_team == suit_calling_team:
            #not Euchred
            if winning_team.tricks_taken_this_round == 5:
                if self.player_going_alone in winning_team.members:
                    #going alone, and called suit successfully
                    points_to_add = 4
                else:
                    points_to_add = 2
            else:
                #normal
                points_to_add = 1
        else:
            #got euchred
            points_to_add = 2
                
        winning_team.add_points(points_to_add)
        
    def determine_round_winner(self):
        return self.teams[0] if self.teams[0].score > self.teams[1
                                                ].score else self.teams[1]
        
    def end_trick(self):
        winning_player = self.determine_trick_winner()
        winning_team = self.get_team_player_is_on(winning_player)
        winning_team.tricks_taken_this_round += 1
        self.clear_cards_on_table()
        
    def end_round(self):
        """ big inclusive method that cleans up the round"""
        self.compensate_round_winner(self, self.determine_round_winner())
        self.clear_cards_on_table()
        [team.reset_tricks_taken() for team in self.teams]
        self.round +=1
        
        self.dealer = self.players[self.round % 4] #player 1 on first call
        self.first_player = self.players[(self.round % 4)+1]
    
    
    def sequence_a_round(self):
        print('round' + self.round)
        #deal cards
        print('dealer is: ' + self.dealer)
        self.deck.deal(self.players)
        [player.sort_hand() for player in self.players]
        #play hand
        for trick_num in range(5):
            for player in self.players:
                #display what's availible
                print(player.name + "'s turn.")
                print("Cards on the table: \n")
                self.print_cards_on_table()
                print("Your Hand: \n")
                player.print_hand()
                
                #they play a card
                chosen_card = player.select_card(player.hand)
                player.remove_card(chosen_card)
                self.add_card(chosen_card)
                
                cls
                input("Pass the computer to the next player. \n")
            self.end_trick()
        self.end_round()
        

def main():
    #make some hello sequence
    
    print('Pass this computer around the circle in order of who goes')
    table = Table(names = [input("Player {} name:".format(i) for i in range(4))]) 
    while no one won
    table.sequence_a_round()
    raise NotImplementedError()        

if __name__ == "__main__":
    main()