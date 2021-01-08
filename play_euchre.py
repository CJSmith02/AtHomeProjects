# -*- coding: utf-8 -*-
"""
Created on Mon May 11 21:57:26 2020
TODO: 
-going alone

@author: Caleb Smith
"""
import euchre_utils
import random
import re
from typing import List, Union

CARD_VALUES_ORDER = ['9','10','J','Q','K','A']
TRUMP_VALUES_ORDER = ['9','10','Q','K','A','LB','RB']
SUITS = ['clubs','spades','hearts','diamonds']
DISABLE_RENEGING = True
#CARD = collections.namedtuple("CARD", ["value", "suit"])

class Card():
    """one card"""
    def __init__(self, value_in:str, suit_in:str) -> None:
        self.owner: Player = None
        if (value_in in CARD_VALUES_ORDER or value_in in TRUMP_VALUES_ORDER) and suit_in in SUITS:
            self.value = value_in
            self.suit = suit_in
        else:
            raise TypeError("value or suit is not valid")

class Player():
    
    """
    a player and their hand of cards instantiated
    """
    def __init__(self, name: str) -> None:
        self.name = name
        self.hand = {s:[] for s in SUITS}
        
    def new_card(self, card: Card) -> None:
        self.hand[card.suit].append(card.value)
        card.owner = self
    
    def remove_card(self, card: Card) -> None:
        self.hand[card.suit].remove(card.value)
        #Don't clear card.owner because I want it to retain that while on the table

    def sort_hand(self, trump: str = "") -> None:
        """
        Sorts cards in terms of power via trump, and changes Js to appropriate bowers
        If trump isn't passed in, it will be sorted not by trump
        """
        left_bower = euchre_utils.get_left_bower(trump) if trump else ""
        # don't sort the trump suit in the for loop cause it could get messed up
        # instead, always sort it after
        for suit in self.hand:
            if left_bower and suit == left_bower.suit:
                #remove old jack, create left bower
                if 'J' in self.hand[suit]:
                    self.hand[suit].remove('J')
                    self.hand[trump].append('LB')
                
            if suit != trump: #suit will return the key which can match with trump
                self.hand[suit].sort(key = CARD_VALUES_ORDER.index)
        
        if trump:
            if 'J' in self.hand[trump]:
                self.hand[trump].remove('J') #undergo name change
                self.hand[trump].append('RB')

            self.hand[trump].sort(key = TRUMP_VALUES_ORDER.index) # TypeError 'list' object is not callable
        
    def print_hand(self, suit_to_print_first:str = "") -> None:
        """use suit_to_print_first for the suit that was led or for trump"""
        if suit_to_print_first: 
            for value in self.hand[suit_to_print_first]:
                print("{} of {}".format(value,suit_to_print_first))
        for suit in self.hand:
            if suit != suit_to_print_first:
                for value in reversed(self.hand[suit]): #print it most powerful first
                    print("{} of {}".format(value,suit))
    
    def select_card(self, options: Union[dict, list], suit_to_follow: str = '', trump: str = '') -> Card:
        """ options is the list OR dictionary of lists (hand) from which a valid 
        card can be drawn. Show the player the options PREVIOUSLY; this asks them to type
        the one they want, and tells them they can't have one they can't have
        Also prevents reneging
        """
        prevent_reneging:bool = DISABLE_RENEGING and suit_to_follow and trump
        
        answer = input("What card do you want to play?")
        value_match = re.search('9|10|J|Q|K|A|LB|RB', answer.upper())
        suit_match = re.search('diamonds|hearts|spades|clubs', answer.lower())
        if value_match and suit_match: # if they exist
            attempt = Card(value_match.group(0),suit_match.group(0))
            attempt.owner = self #I wish this line went elsewhere, but that would require massive refactoring
            if type(options) == dict: #a hand
                if attempt.value in options[attempt.suit]:
                    if prevent_reneging:
                        if attempt.suit != suit_to_follow and len(self.hand[suit_to_follow]) > 0:
                            # They're not following suit, they're reneging
                            print("You have to follow suit if you have those cards in your hand. Reneging is disabled")
                            return self.select_card(options, suit_to_follow, trump)
                        else:
                            return attempt
                    else:
                        return attempt
                else:
                    print("Try again. That card is not an option.")
                    return self.select_card(options)
        else:
            print("Try again. You mistyped a card. Make sure to spell out " +
                  "the suit, like 'k clubs'")
            return self.select_card(options) # yes it's recursion. it's ok though


PLAYERS = List[Player]
    
class Deck():
    def __init__(self) -> None:
        self.cards = []
        #generate the cards
        for suit in SUITS:
            for value in CARD_VALUES_ORDER:
                self.cards.append(Card(value,suit))
        # shuffle them
        random.shuffle(self.cards)
    
    def get_card(self) -> Card:
        return self.cards.pop()
    
    def deal(self, players: PLAYERS) -> None:
        num_cards_to_deal = iter([3,2,3,2,2,3,2,3])
        for i in range(2): # go around twice
            for player in players: #at each player
                for j in range(next(num_cards_to_deal)): #deal multiple cards
                    card = self.get_card()
                    player.new_card(card)
        [player.sort_hand() for player in players]


class Team():
    def __init__(self, player1: Player, player2: Player) -> None:
        self.members = [player1, player2]
        self.score = 0
        self.tricks_taken_this_round = 0
    
    def reset_tricks_taken(self) -> None:
        self.tricks_taken_this_round = 0

    def add_points(self, points_to_add) -> None:
        self.score += points_to_add
    
    
class Table():
    
    """
    the class that governs everything that happens
    """
    def __init__(self, names) -> None:
        self.players: PLAYERS = [Player(name) for name in names]
        self.teams = [Team(self.players[i], self.players[i+2]) for i in range(
                2)]
        
        self.dealer: Player = self.players[0]
        self.first_player: Player = self.players[1]
        self.deck = Deck()
        
        #round-specific variables that change
        self.round: int = 1
        self.cards_on_table: List[Card] = []
        self.trump: str = ''
        self.player_going_alone: Player = None
        self.player_that_called_suit: Player = None
        self.suit_to_follow: str = ''

    def recreate_deck(self) -> None:
        del self.deck
        self.deck = Deck() #hopefully this works
               
    def add_card(self, card: Card) -> None:
        self.cards_on_table.append(card)
        
    def get_team_player_is_on(self, player:Player) -> Team:
        for team in self.teams:
            if player in team.members:
                return team
    
    def get_other_team(self, team1) -> Team:
        for team in self.teams:
            if team != team1: # i thiiiink '==' better than 'is' here
                return team
    
    def clear_cards_on_table(self) -> None:
        self.cards_on_table.clear()
        
    def print_cards_on_table(self) -> None:
        if self.cards_on_table: # if it's not empty
            print("\nCards on the table:")
            for card in self.cards_on_table:
                if card.owner:
                    print("{} played: {} of {}".format(card.owner.name, card.value, card.suit))
                else:
                    print("{} of {}".format(card.value, card.suit))
        else:
            print("\nThere are no cards on the table")
        
    def determine_trick_winner(self) -> Player:
        """
        returns the player object of who played the highest card based on self properties
        """
        winning_card = euchre_utils.get_best_card(self.cards_on_table,
                                                  self.trump)
        return winning_card.owner
        
    def compensate_round_winner(self, winning_team: Team) -> None:
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
        
    def determine_round_winner(self) -> Team:
        return self.teams[0] if self.teams[0].tricks_taken_this_round > self.teams[1
                                                ].tricks_taken_this_round else self.teams[1]
        
    def end_trick(self) -> None:
        winning_player = self.determine_trick_winner()
        self.first_player = winning_player
        winning_team = self.get_team_player_is_on(winning_player)
        winning_team.tricks_taken_this_round += 1
        self.clear_cards_on_table()
        self.suit_to_follow = ''
        input("{} and {} won the trick! Pass the computer to {} to start the next trick".format(
            winning_team.members[0].name, winning_team.members[1].name, winning_player.name))
        euchre_utils.clear_screen()
        
    def end_round(self) -> None:
        """ big inclusive method that cleans up the round"""
        winning_team = self.determine_round_winner()
        self.compensate_round_winner(winning_team)
        self.clear_cards_on_table()
        self.recreate_deck()
        [team.reset_tricks_taken() for team in self.teams]
        self.trump = "" #so that print_status_update's if clause about initialize trump holds
        self.round +=1
        
        self.dealer = self.players[(self.round % 4)-1] #player 0 on round 1
        self.first_player = self.players[(self.round % 4)] #player 1 on round 1, 2 on round 2
        input("{} and {} won the round!".format(winning_team.members[0].name, winning_team.members[1].name))
        euchre_utils.clear_screen()

    def print_status_update(self, player: Player = None, its_their_turn: bool = False) -> None:
        """
        prints round, dealer, score and tricks for each team, trump, and if anyone is going alone
        """
        print('ROUND {}, TRICK {}'.format(self.round, 
        self.teams[0].tricks_taken_this_round + self.teams[1].tricks_taken_this_round + 1))

        name_len = 9 + max(len(self.players[0].name) + len(self.players[2].name), 
                    len(self.players[1].name) + len(self.players[3].name))
        print("".ljust((name_len +20)//2, "-") + "Score:" + "".ljust((name_len +20)//2, "-"))
        print("Team".ljust(name_len) + "Score  " + "Tricks this round")
        print("{p0} and {p2}".format(p0=self.players[0].name, p2=self.players[2].name).ljust(name_len)
            + "{}".format(self.teams[0].score).ljust(7) + "{}".format(self.teams[0].tricks_taken_this_round))
        print("{p1} and {p3}".format(p1=self.players[1].name, p3=self.players[3].name).ljust(name_len)
            + "{}".format(self.teams[1].score).ljust(7) + "{}".format(self.teams[1].tricks_taken_this_round))
        
        print('\nDealer is: ' + self.dealer.name)
        if player:
            print("Player is: " + player.name)
        if self.trump:
            print("\nTrump is {t}, called by {p}".format(t=self.trump,
                p=self.player_that_called_suit.name))

            if self.cards_on_table:
                print("{} was led".format(self.cards_on_table[0].suit))
        
        if self.player_going_alone:
            print("{} is going alone".format(self.player_going_alone))

        if self.cards_on_table: #if there are any cards on the table, say it
            self.print_cards_on_table()
        if its_their_turn:
            if player:
                print("\n{}, it is your turn".format(player.name))
            else:
                print("\nIt is your turn")
        if player: #if the player is passed in, print their hand
            print("\n{}, these are your cards:".format(player.name))

            if self.suit_to_follow: 
                player.print_hand(self.suit_to_follow) #print the suit to follow first
            else:
                player.print_hand(self.trump)  #if there's no suit on the table, use trump. If trump ="", oh well
        print("\n")

    def initialize_trump(self) -> None:
        """go around the table to see who wants to call trump"""
        input("Time to decide trump. Pass the computer to " + self.first_player.name)
        euchre_utils.clear_screen()
        starting = self.players.index(self.first_player)
        i=starting

        self.add_card(self.deck.get_card())
        
        while i <= starting+7:
            player = self.players[i%4]
            self.print_status_update(player)
            face_up_card: Card = self.cards_on_table[0]

            if i <= starting+3: #first time around
                answer = euchre_utils.get_yes_no("Do you want the dealer"+
                 " to pick up the card on the table and that card to" +
                 " become trump?".format(player.name))
                if answer:
                    #alone_answer = euchre_utils.get_yes_no("Do you want to go alone?")
                    euchre_utils.clear_screen()
                    input("\nOK, Announce that {} is trump. Pass the computer to the dealer({})".format(
                        face_up_card.suit, self.dealer.name))
                    euchre_utils.clear_screen()
                    self.dealer.new_card(face_up_card)
                    self.clear_cards_on_table()
                    self.trump = face_up_card.suit
                    self.player_that_called_suit = player
                    
                    #dealer chooses which cards to remove
                    self.dealer.sort_hand(self.trump)
                    self.print_status_update(self.dealer)
                    print("Dealer, {} told you to pick it up. ".format(player.name)+
                    "Which card in your hand do you want to remove?")
                    self.dealer.remove_card(self.dealer.select_card(self.dealer.hand))
                    euchre_utils.clear_screen()
                    input("Pass the computer to {} to start the round".format(self.first_player.name))
                    euchre_utils.clear_screen()
                    break
                else: 
                    euchre_utils.clear_screen()
                    input("\nPass the computer to {}".format(self.players[(i+1)%4].name))
                    euchre_utils.clear_screen()
            
            else: #second time around, choose which suit to be trump
                response = euchre_utils.get_answer_no("Do you want to select the trump suit?"+
                    " If so, say which. You're playing 'stick the dealer'\n", "diamonds|hearts|spades|clubs")
                if response and response != face_up_card.suit: #if they say an availible suit
                    print("OK, {} is Trump. Pass the computer to {} to start the round".format(
                        response, self.first_player.name))
                    self.trump = response
                    self.player_that_called_suit = player
                    self.clear_cards_on_table()
                    break
                elif response == face_up_card.suit:
                    input("Sorry, you can't choose the suit that was initially face up. Try again")
                    i-=1 # loop around to the same player again to give another chance
                elif i == starting+7: #STICK THE DEALER
                    #this if clause needs to come after the first two to take lower precedence
                    input("You're playing 'stick the dealer', so the dealer has to choose a suit.")
                    i-=1
                else: #empty string, they said no
                    euchre_utils.clear_screen()
                    input("\nOK, pass the computer to {}".format(self.players[(i+1)%4].name))
                    euchre_utils.clear_screen()
                
            euchre_utils.clear_screen()
            i+=1
        euchre_utils.clear_screen()
        #sort everybodys hands according to trump
        [player.sort_hand(self.trump) for player in self.players]
        
    def sequence_a_round(self) -> None:
        #deal cards
        self.deck.deal(self.players)

        self.initialize_trump()

        #play hand
        for trick_num in range(5):
            for i in range(self.players.index(self.first_player),
                        self.players.index(self.first_player) +4):
                player = self.players[i%4]
                
                self.print_status_update(player, True)
                if len(self.cards_on_table) >0:
                    self.suit_to_follow = self.cards_on_table[0].suit

                #they play a card
                chosen_card = player.select_card(player.hand, self.suit_to_follow, self.trump)
                player.remove_card(chosen_card)
                self.add_card(chosen_card)
                
                euchre_utils.clear_screen()
                print("OK {}, you played the {} of {}".format(
                    player.name, chosen_card.value, chosen_card.suit))
                if i != (self.players.index(self.first_player) + 3): # don't to it the last time
                    input("Pass the computer to the next player. \n")
                    euchre_utils.clear_screen()
            self.end_trick()
        self.end_round()

    def has_someone_won(self) -> bool:
        for team in self.teams:
            if team.score >=10:
                return True
        return False
    

def main():
    #make some hello sequence
    
    print('Pass this computer around the circle in order of who goes')
    euchre_utils.clear_screen()
    player_names = []
    [player_names.append(input("Player {} name:".format(i))) for i in range(4)]
    table = Table(names = player_names)
    euchre_utils.clear_screen()
    
    while not table.has_someone_won():
        table.sequence_a_round()
    

if __name__ == "__main__":
    main()