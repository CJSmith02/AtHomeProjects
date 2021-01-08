# -*- coding: utf-8 -*-ghx.p
"""
Created on Mon May 11 20:34:45 2020

@author: Caleb Smith
"""
#import collections
import os
from play_euchre import Card #yes this is bad but it works for some reason
import re
from typing import List

#CARD = collections.namedtuple("CARD", ["value", "suit"])
HAND = {'clubs': [],'spades':[],'hearts':[],'diamonds':[]}
CARD_VALUES_ORDER = ['9','10','J','Q','K','A']
TRUMP_VALUES_ORDER = ['9','10','Q','K','A','LB','RB']
SUITS = ['clubs','spades','hearts','diamonds']


def get_card_color(card: Card) -> str:
    if card.suit in ["hearts","diamonds"]:
        return "red"
    elif card.suit in ["clubs","spades"]:
        return "black"
    else:
        raise ValueError('suit is not valid')
        
def get_left_bower(trump_suit: str) -> Card:
    """
    Given the suit that is trump, returns the equivelent left bower
    """
    left_bowers = {'hearts':'diamonds', 'diamonds':'hearts', 'spades':'clubs',
                   'clubs':'spades'}
    return (Card('J', left_bowers[trump_suit]))

def compare_cards(card1: Card, card2: Card, trump: str, suit_to_follow: str) -> Card:
    """
    input two cards and what suit is trump
    returns the higher card
    
    Requires that cards have been sorted in their hand b/c RB LB
    """
    
    if card1.suit == card2.suit == trump:
            return card1 if TRUMP_VALUES_ORDER.index(card1.value
            ) > TRUMP_VALUES_ORDER.index(card2.value) else card2
        
    elif card1.suit == card2.suit != trump:
        return card1 if CARD_VALUES_ORDER.index(card1.value
            ) > CARD_VALUES_ORDER.index(card2.value) else card2
    
    elif card1.suit == trump:
        return card1
    
    elif card2.suit == trump:
        return card2
    
    elif card1.suit == suit_to_follow and card2.suit != suit_to_follow:
        return card1
    
    elif card2.suit == suit_to_follow and card1.suit != suit_to_follow:
        return card2
    
    elif card1.suit == card2.suit != (trump or suit_to_follow):
        raise ValueError("Can't compare cards that aren't trump and are wrong suit")
    
def get_best_card(array_of_cards: List[Card], trump: str) -> Card:
    """
    Returns the most powerful card
    """
    card_to_beat = array_of_cards[0]
    suit_to_follow = array_of_cards[0].suit
    for i in range(1, len(array_of_cards)): # cause already took the first one
        card_to_beat = compare_cards(card_to_beat, array_of_cards[i],
                                     trump, suit_to_follow)
    return card_to_beat
    
def clear_screen() -> None:
    os.system('cls||clear')
    
def get_yes_no(question: str) -> bool:
    answer = input(question)
    if "Y" in answer.upper() or "TRUE" in answer.upper():
        return True
    elif "N" in answer.upper() or "FALSE" in answer.upper():
        return False
    else:
        print("Invalid input; this is a yes or no question. Try again")
        get_yes_no(question)

def get_answer_no(question: str, regex: str) -> str:
    """
    the user enters either an answer, or No
    @param regex es just the regex for the options, leave the 'no' up to this function
    @returns empty string, or whatever the user entered that matched the regex (as a string)
    dynamically typed is OP
    """
    answer = input(question)
    match = re.search(regex, answer.lower())
    if "NO" in answer.upper() or "FALSE" in answer.upper():
        return ""
    elif match:
        return match.group(0)
    else:
        print("Sorry, your answer isn't valid. Please try again.")
        get_answer_no(question, regex)
