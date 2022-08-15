#!/usr/bin/env python

# BLACKJACK
### REV1: Refactoring, adding and integrating "Hand" object
### REV2: Compatibility with cmd/powershell/Linux shells, roll clear() into display_table()
### REV3: Cleanup of object reinitialization
### REV4: Add insurance capability
### REV5: Add split hand capability
### REV6: Use structural pattern matching (requires a 3.10 runtime or higher)
### REV7: Support decimals for some reason
### REV8: Ensure insurance pays out once
### REV9: Dealer has finite pool of chips for possible future 'win' condition
### REV10: Large refactor, place_bets() in Bankroll and play_hands(), double_down() & split() in Player
### REV11: Support for playing multiple hands from the start
### REV12: Refactoring: hit(), double_down() & split() in Hand, insurance routine in Player
### REV13: Touched up play_hands() routine, made split not so buggy
### REV14: Major refactor, all revisions in the repo moving forward

from os import system, name
from re import search
from time import sleep
from random import shuffle

class Card:

    SUITS = ('♠','♣','♦','♥')
    RANKS = ('2','3','4','5','6','7','8','9','10','J','Q','K','A')
    VALUES = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':10,'Q':10,'K':10,'A':11}
    
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = self.VALUES[rank]

    # Going with representing each card more visually than "THREE OF CLUBS"
    def __str__(self):
        if self.suit in ('♦','♥'):
            return '|' + '\033[31m' + self.rank + self.suit + '\033[39m' + '|'
        return '|' + self.rank + self.suit + '|'
    
class Deck:
    
    # Populate deck
    def __init__(self):
        self.all_cards = []
        for suit in Card.SUITS:
            for rank in Card.RANKS:
                self.all_cards.append(Card(rank,suit))
    
    # Randomize deck
    def shuffle(self):
        shuffle(self.all_cards)

    # Remove card from "top" of deck.
    # pop() would take from the bottom I guess. OH WELL
    def deal_one(self):
        return self.all_cards.pop()

class Player:

    def __init__(self, name, is_dealer):
        self.name = name
        self.is_dealer = is_dealer
        self.insurance_open = False
        self.hands = []

    def __str__(self):
        return f"**{self.name.upper()}**"

    def victory_message(self):
        print('You spot the dealer gesturing subtly. Sure enough, it\'s not long before a cohort of armed security is upon you.')
        print('\"Looks like we got an advantage player, boys.\"')
        print('As you are roundly beaten within an inch of your life, you catch a fleeting glimpse of your hard-won winnings and sigh. Now how will you pave the driveway?\n')
        print(f'{self.name} WINS!')

    def ins_payout(self, bet, bankroll, house):
        bankroll.credit(bet * 3)
        house.debit(bet * 2)
        return f"{self.name} wins the insurance bet. Payout is 2:1.\n{self.name} wins ${bet * 2:.2f}."

    def ins_loss(self, bet, house):
        house.credit(bet)
        return f"{self.name} loses the insurance bet.\nHouse wins ${bet:.2f}."

    def get_insurance_flag(self):
        return self.insurance_open

    def set_insurance_flag(self, flag):
        self.insurance_open = flag

    def add_hand(self, idx, new_hand):
        self.hands.insert(idx, new_hand)

    def setup_hands(self, bankroll):
        num_hands = ''
        while not search('^\d$', num_hands):
            try:
                num_hands = input(f'{self.name} has ${bankroll.get_chips():.2f} in chips.\nPlay how many hands? (Max: 4)\n')
                if int(num_hands) > 4:
                    raise ValueError('Max four hands in play.')
            except:
                print('Invalid Input.')
                num_hands = ''
        return num_hands

    def play_hands(self, cur_deck, num_hands, bankroll=None, house=None):
        hand_ct = 0

        # Dealer's play
        if self.is_dealer:
            d_hand = self.hands[0]
            d_hand.reveal()
            display_table(f'Dealer has {dealer_hand.score}.', 1)
            while d_hand.get_score() < 17:
                d_hand.draw(cur_deck)
                display_table('Dealer hits.', 1)
                if d_hand.is_bust:
                    display_table('Dealer busts.')
            d_hand.resolve()
            
        # Player's play
        else:
            while hand_ct < num_hands:
                hand = self.hands[hand_ct] if not self.hands[hand_ct].is_split else self.hands[hand_ct - 1]
                hand.in_play = True
                display_table(f'Action to {self.name}.')

                # Can't double down on pocket aces, can only split pairs to a max of 4 hands
                double_legal = False if all(card.rank == 'A' for card in hand.cards) else True
                insurance_legal = self.get_insurance_flag() and bankroll.get_chips() > 0
                split_legal = True if hand.cards[0].rank == hand.cards[1].rank and num_hands < 4 else False

                prompt = "What will you do? \n 1. Hit \n 2. Stand \n 3. Double Down \n 4. Insurance \n 5. Split \n"
                choice = '' ; turn_ct = 0
                while hand.get_score() <= 21:
                    # Re-check legality, grey out illegal options
                    insurance_legal = self.get_insurance_flag()
                    if num_hands > 3: 
                        split_legal = False 
                    if not split_legal or turn_ct > 0:
                        prompt = prompt.replace('5. Split', '\033[90m' + '5. Split' + '\033[39m')
                    if not insurance_legal:
                        prompt = prompt.replace('4. Insurance', '\033[90m' + '4. Insurance' + '\033[39m')
                    if not double_legal or turn_ct > 0:
                        prompt = prompt.replace('3. Double Down', '\033[90m' + '3. Double Down' + '\033[39m')

                    choice = input(prompt)
                    match choice:
                        # Hit
                        case '1':
                            hand.draw(cur_deck)
                            display_table(f'{self.name} hits.', 0.5)
                            if hand.is_bust:
                                hand.bust(bankroll, house, bankroll.get_bet_amt(hand_ct), hand_ct)
                                hand.resolve()
                                display_table(f'BUST! {hand.idx_to_word(hand_ct).capitalize()} bet is forfeit.', 1)
                        # Stay
                        case '2':
                            display_table(f'{self.name} stands.', 1)
                            break
                        # Double down on any two cards, draw once
                        case '3' if double_legal and turn_ct == 0:
                            doubled = hand.double_down(hand_ct, cur_deck, bankroll)
                            if not doubled:
                                continue
                            display_table(f'{self.name} doubles down.', 0.5)
                            if hand.is_bust:
                                hand.bust(bankroll, house, bankroll.get_bet_amt(hand_ct), hand_ct)
                                hand.resolve()
                                display_table(f'BUST! {hand.idx_to_word(hand_ct).capitalize()} bet is forfeit.', 1)
                            break
                        # Buy insurance (if dealer showing A)
                        case '4' if insurance_legal and bankroll.get_chips() > 0:
                            insured = bankroll.buy_insurance(bankroll.get_total_bet_amt())
                            if not insured:
                                continue
                            self.set_insurance_flag(False)
                            display_table('Insurance purchased.', 1)
                            break
                        # Split a pair
                        case '5' if split_legal and len(hand.cards) == 2:
                            spl_hand = hand.split(hand_ct, cur_deck, bankroll)
                            if not isinstance(spl_hand, Hand):
                                continue
                            self.add_hand(hand_ct - 1, spl_hand)
                            num_hands += 1
                            display_table(f'{self.name} splits a pair.')
                        case _:
                            display_table('Invalid Input.')
                            continue
                    turn_ct += 1
                # Move on to next hand
                hand.in_play = False
                hand_ct += 1 

    def resolve_hands(self, dealer, bankroll, house):
        d_hand = dealer.hands[0]
        ins_bet = bankroll.get_ins_bet_amt()
        insured = True if ins_bet > 0 else False
        results = [ '\n**RESULTS**' ]

        # Pay out 2:1 on insurance wager
        if insured:
            if d_hand.is_blackjack:
                d_hand.reveal()
                display_table('Insurance pays out.')
                results.append(player_one.ins_payout(ins_bet, player_one_chips, house_chips))
            else:
                display_table('Insurance is forfeit.')
                results.append(player_one.ins_loss(ins_bet, house_chips))
            bankroll.ins_resolve()

        for idx, hand in enumerate(player_one.hands):
            bet = bankroll.get_bet_amt(idx)
            # Player bj pays out 3:2; wash if dealer also bj 
            if hand.is_blackjack:
                if not d_hand.is_blackjack:
                    results.append(hand.blackjack(bankroll, house, bet, idx))
                    hand.resolve()
                    continue
                d_hand.reveal()
                results.append(hand.push(bankroll, bet, idx))
                hand.resolve()
                continue
            # Yep, dealer still wins with a blackjack even if player stands at 21
            elif d_hand.is_blackjack:
                d_hand.reveal()
                results.append(d_hand.blackjack(bankroll, house, bet, idx))
                hand.resolve()
                continue
            # Player over 21: bet is forfeit
            if hand.is_bust:
                results.append(f'{player_one.name} {hand.idx_to_word(idx)} hand busts.\nHouse wins ${bet:.2f}.')
            else:
                if not d_hand.is_resolved:
                    dealer.play_hands(new_deck, 1)
                if d_hand.is_bust:
                    results.append(d_hand.bust(bankroll, house, bet, idx))
                elif hand.get_score() > d_hand.get_score():
                    results.append(hand.won(bankroll, house, bet, idx))
                elif hand.get_score() < d_hand.get_score():
                    results.append(hand.lost(house, bet, idx))
                else:
                    results.append(hand.push(bankroll, bet, idx))
            hand.resolve()
       
        display_table('Round over.')
        return results

class Hand:

    NUM_MAP = {0:'first',1:'second',2:'third',3:'fourth'}

    def __init__(self, owner):
        self.owner = owner
        self.score = 0
        self.cards = []
        self.in_play = False
        self.is_resolved = False
        self.is_blackjack = False
        self.is_bust = False
        self.is_doubled_down = False
        self.is_split = False
        self.is_hidden = False
        if self.owner.is_dealer:
            self.is_hidden = True

    def __str__(self):
        hand_repr = ''
        for idx, card in enumerate(self.cards):
            # Hide dealer's first card
            if idx == 0 and self.is_hidden:
                hand_repr += '|??|\n'
            else:
                # String multiplication to make that hand POP
                hand_repr += ' ' * idx + str(card) + '\n'
        return f'Score: {(self.score if not self.is_hidden else "?")} {("← In-Play" if self.in_play else "")}\n{hand_repr}'

    def resolve(self):
        self.is_resolved = True

    def reveal(self):
        self.is_hidden = False

    def idx_to_word(self, idx):
        return self.NUM_MAP[idx]

    def calc_score(self):
        soft_count = 0
        total = 0

        # Count aces in soft hand
        for card in self.cards:
            total += card.value
            if card.rank == 'A':
                soft_count += 1
        while total > 21 and soft_count > 0:
            total -= 10
            soft_count -= 1
        self.score = total

        # Set flags for blackjack / bust
        if len(self.cards) == 2 and self.score == 21:
            self.is_blackjack = True
        elif self.score > 21:
            self.is_bust = True

    def get_score(self):
        return self.score

    def get_doubled_flag(self):
        return self.is_doubled_down

    def set_doubled_flag(self, flag):
        self.is_doubled_down = flag

    def add_cards(self, new_cards):
        if type(new_cards) == type([]):
            self.cards.extend(new_cards)
        self.cards.append(new_cards)

    def draw(self, cur_deck):
        self.add_cards(cur_deck.deal_one())
        self.calc_score()

    def double_down(self, cur_idx, cur_deck, bankroll):
        enough = bankroll.bet(bankroll.get_bet_amt(cur_idx))
        # Players need enough money to double down
        if enough:
            self.set_doubled_flag(True)
            bankroll.set_bet_amt(bankroll.get_bet_amt(cur_idx) * 2, cur_idx)
            self.draw(cur_deck)
            return True
        return False

    def split(self, cur_idx, cur_deck, bankroll):
        enough = bankroll.bet(bankroll.get_bet_amt(cur_idx))
        # Player must have enough to bet the same amount into the second hand
        if enough:
            # New hand object, populate with second card from first hand
            subhand = Hand(self.owner)
            subhand.add_cards(self.cards.pop())
            display_table(f'{self.owner.name} splits a pair.')
            # Each hand is dealt an additional card
            for subhand in [ self, subhand ]:
                subhand.draw(cur_deck)
                display_table(f'{self.owner.name} splits a pair.', 0.25)
            
            bankroll.add_bet(cur_idx - 1, bankroll.get_bet_amt(cur_idx))
            self.is_split = True
            return subhand
        # No money no hand
        return None

    def blackjack(self, bankroll, opfor, bet, idx):
        if not self.owner.is_dealer:
            bankroll.credit(bet * 2.5)
            opfor.debit(bet * 1.5)
            return f"{self.owner.name} {self.idx_to_word(idx)} hand BLACKJACK! Payout is 3:2.\n{bankroll.owner} wins ${bet * 1.5:.2f}."
        opfor.credit(bet)
        return f"{self.owner.name} BLACKJACK! Dealer takes the pot.\n{opfor.owner} wins ${bet:.2f}."

    def bust(self, bankroll, opfor, bet, idx):
        if not self.owner.is_dealer:
            opfor.credit(bet)
            return f"{self.owner.name} {self.idx_to_word(idx)} hand busts! Dealer takes the pot.\n{opfor.owner} wins {bet:.2f}."
        bankroll.credit(bet * 2)
        opfor.debit(bet)
        return f"{self.owner.name} busts! Payout is 1:1.\n{bankroll.owner} wins ${bet:.2f}."

    def push(self, bankroll, bet, idx):
        bankroll.credit(bet)
        return f"{self.owner.name} {hand.idx_to_word(idx)} hand PUSH!\n{self.owner.name} is returned his {hand.idx_to_word(idx)} bet."

    def lost(self, house, bet, idx):
        house.credit(bet)
        return f"{self.owner.name} loses the {self.idx_to_word(idx)} hand! Dealer takes the pot.\n{house.owner} wins ${bet:.2f}."

    def won(self, bankroll, house, bet, idx):
        bankroll.credit(bet * 2)
        house.debit(bet)
        return f"{self.owner.name} wins the {self.idx_to_word(idx)} hand! Payout is {('2' if self.is_doubled_down else '1')}:1.\n{self.owner.name} wins ${bet:.2f}."

class Bankroll:

    INITIAL_CHIPS = 1000
    HOUSE_CHIPS = 10000

    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance
        self.bets = []
        self.total_bet_amt = 0
        self.ins_bet_amt = 0
        self.ins_resolved = False

    def __str__(self):
        if self.owner == 'House':
            return f'House has ${self.balance:,.2f} left.'
        return f'{self.owner} has ${self.balance:,.2f} in chips.'

    def get_chips(self):
        return self.balance

    def set_chips(self, amount):
        self.balance = amount

    # Main bets
    def get_bet_amt(self, idx):
        return self.bets[idx]

    def set_bet_amt(self, amount, idx):
        self.bets[idx] = amount

    def get_total_bet_amt(self):
        return self.total_bet_amt

    def calc_total_bet_amt(self):
        self.total_bet_amt = sum(map(float,self.bets))

    # Insurance bets
    def get_ins_bet_amt(self):
        return self.ins_bet_amt

    def set_ins_bet_amt(self, amount):
        self.ins_bet_amt = amount

    def ins_resolve(self):
        self.ins_resolved = True

    def add_bet(self, idx, bet):
        self.bets.insert(idx, bet)

    # Lose moni
    def bet(self, amount):
        if (self.balance - amount) >= 0:
            self.balance -= amount
            print(f'{self.owner} bets ${amount:.2f}.')
            return True
        display_table('Not enough chips.')
        return False

    def debit(self, amount):
        self.balance -= amount

    # Gib moni
    def credit(self, amount):
        self.balance += amount

    # Betting Phase
    def place_bets(self, hand, idx, num_hands):
        bet_amt = ''
        while not search('^\d+(\.\d{1,2})?$', bet_amt):
            try:
                if num_hands > 1:
                    bet_amt = input(f'Bet towards {hand.idx_to_word(idx)} hand: (Bankroll: ${self.balance:.2f})\n') 
                else:
                    bet_amt = input(f'Place your bet: (Bankroll: ${self.balance:.2f})\n')    
                if bet_amt[::-1].find('.') > 2:
                    raise ValueError('Max two decimal places.')
                if self.bet(float(bet_amt)):
                    self.add_bet(idx, float(bet_amt))
                    self.set_bet_amt(float(bet_amt), idx)
            except:
                print('Invalid Input.')
                bet_amt = ''

    # Insure yoself
    def buy_insurance(self, bet_amt):
        ins_bet_amt = ''
        while not search('^\d+(\.\d{1,2})?$', ins_bet_amt):
            try:
                ins_bet_amt = input(f'Purchase how much insurance? (Limit: ${0.5 * float(bet_amt):.2f})\n')
                if ins_bet_amt[::-1].find('.') > 2:
                    raise ValueError('Max two decimal places.')
                if float(ins_bet_amt) > 0.5 * float(bet_amt):
                    display_table('Insurance bet cannot be more than 50% of total bet.')
                    ins_bet_amt = ''
                    continue
                if self.bet(float(ins_bet_amt)):
                    self.set_ins_bet_amt(float(ins_bet_amt))
                    return True
                return False
            except:
                display_table('Invalid Input.')
                ins_bet_amt = ''

    # Check for game over
    def let_it_ride(self):
        if self.balance == 0:
            print(f'{self.owner} is bankrupt. {self.owner} LOSES!')
            return False

        cont = input('Continue Playing y/[n]?\n')
        if search('^(y|Y).*', cont):
            clear()
            return True
        # Game over
        print(f'{self.owner} takes his ${self.balance:.2f} and goes home.')
        return False

# Clear output on Windows/Linux shell
def clear(): 
    system('cls' if name == 'nt' else 'clear') 

# Display game state
def display_table(action = '', delay = 0):
    clear()
    print(player_one_chips)
    print(house_chips) 
    for idx, hand in enumerate(player_one.hands):
        if not hand.is_resolved:
            print(f'{hand.idx_to_word(idx).upper()} HAND BET: ${player_one_chips.get_bet_amt(idx):.2f}')
    if player_one_chips.get_ins_bet_amt() > 0 and not player_one_chips.ins_resolved:
        print(f'INSURANCE: ${player_one_chips.get_ins_bet_amt():.2f}')
    print()
    print(player_one)
    for hand in player_one.hands:
        print(str(hand)) 
    print(dealer)
    print(str(dealer_hand))
    if action:
        print(action)
    sleep(delay)

# Populate players
player_one = Player(input("Enter your name: "), False)
player_one_chips = Bankroll(player_one.name, Bankroll.INITIAL_CHIPS)

dealer = Player('Dealer', True)
house_chips = Bankroll('House', Bankroll.HOUSE_CHIPS)

game_on = True
while(game_on):
    # Re-initialize object variables
    Player.__init__(player_one, player_one.name, False)
    Player.__init__(dealer, dealer.name, True)
    Bankroll.__init__(player_one_chips, player_one.name, player_one_chips.get_chips())
    Bankroll.__init__(house_chips, 'House', house_chips.get_chips())

    # Setup deck + dealer
    new_deck = Deck()
    new_deck.shuffle()
    dealer_hand = Hand(dealer)
    dealer.add_hand(0, dealer_hand)
    
    # Bettin phase
    num_hands = player_one.setup_hands(player_one_chips)
    for i in range(int(num_hands)):
        new_hand = Hand(player_one)
        player_one_chips.place_bets(new_hand, i, int(num_hands))
        player_one.add_hand(i, new_hand)
    player_one_chips.calc_total_bet_amt()
    
    # Deal in the proper order (one each hand, Dealer's hole, one each hand, Dealer's faceup)
    for i in range(2):    
        for hand in player_one.hands:
            hand.draw(new_deck)
            display_table('Dealing...', 0.25)
        dealer_hand.draw(new_deck)
        display_table('All cards dealt.')   
    # Check whether insurance is open (faceup A for dealer)
    if dealer_hand.cards[1].rank == 'A':
        player_one.set_insurance_flag(True)

    # Play text game
    player_one.play_hands(new_deck, int(num_hands), player_one_chips, house_chips)

    # Evaluate results
    results = player_one.resolve_hands(dealer, player_one_chips, house_chips)
    for msg in results:
        print(msg)
        sleep(0.125)

    # Good luck with that
    if house_chips.get_chips() <= 0:
        player_one.victory_message()
        break

    # Clean up after ourselves
    del new_deck
    del dealer_hand
    for hand in player_one.hands: del hand

    game_on = player_one_chips.let_it_ride()
    continue

print("\n**GAME OVER**")
sleep(1.5)
