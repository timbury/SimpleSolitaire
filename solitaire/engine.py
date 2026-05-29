from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Dict, List, Optional

SUITS = ["♠", "♥", "♦", "♣"]
RANK_LABELS = {1: "A", 11: "J", 12: "Q", 13: "K"}


@dataclass(frozen=True)
class Card:
    rank: int
    suit: str

    @property
    def color(self) -> str:
        return "red" if self.suit in {"♥", "♦"} else "black"

    @property
    def label(self) -> str:
        rank_text = RANK_LABELS.get(self.rank, str(self.rank))
        return f"{rank_text}{self.suit}"


@dataclass
class TableauCard:
    card: Card
    face_up: bool = False


class KlondikeGame:
    def __init__(self, seed: Optional[int] = None) -> None:
        self.stock: List[Card] = []
        self.waste: List[Card] = []
        self.foundations: Dict[str, List[Card]] = {suit: [] for suit in SUITS}
        self.tableau: List[List[TableauCard]] = [[] for _ in range(7)]
        self.new_game(seed=seed)

    def new_game(self, seed: Optional[int] = None) -> None:
        deck = [Card(rank, suit) for suit in SUITS for rank in range(1, 14)]
        rng = random.Random(seed)
        rng.shuffle(deck)

        self.waste = []
        self.foundations = {suit: [] for suit in SUITS}
        self.tableau = []

        for pile_index in range(7):
            pile: List[TableauCard] = []
            for card_index in range(pile_index + 1):
                card = deck.pop()
                pile.append(TableauCard(card=card, face_up=card_index == pile_index))
            self.tableau.append(pile)

        self.stock = deck

    def draw_from_stock(self) -> bool:
        if self.stock:
            self.waste.append(self.stock.pop())
            return True
        if self.waste:
            while self.waste:
                self.stock.append(self.waste.pop())
            return True
        return False

    def move_waste_to_foundation(self, target_suit: Optional[str] = None) -> bool:
        if not self.waste:
            return False
        card = self.waste[-1]
        if target_suit and target_suit != card.suit:
            return False
        if not self._can_move_to_foundation(card):
            return False

        self.waste.pop()
        self.foundations[card.suit].append(card)
        return True

    def move_tableau_to_foundation(self, source_pile: int, target_suit: Optional[str] = None) -> bool:
        if not self._valid_tableau_index(source_pile) or not self.tableau[source_pile]:
            return False

        entry = self.tableau[source_pile][-1]
        if not entry.face_up:
            return False
        card = entry.card

        if target_suit and target_suit != card.suit:
            return False
        if not self._can_move_to_foundation(card):
            return False

        self.tableau[source_pile].pop()
        self.foundations[card.suit].append(card)
        self._flip_tableau_top(source_pile)
        return True

    def move_foundation_to_tableau(self, source_suit: str, target_pile: int) -> bool:
        if source_suit not in self.foundations:
            return False
        if not self._valid_tableau_index(target_pile):
            return False
        if not self.foundations[source_suit]:
            return False

        card = self.foundations[source_suit][-1]
        if not self._can_place_on_tableau(card, target_pile):
            return False

        self.foundations[source_suit].pop()
        self.tableau[target_pile].append(TableauCard(card=card, face_up=True))
        return True

    def move_waste_to_tableau(self, target_pile: int) -> bool:
        if not self.waste or not self._valid_tableau_index(target_pile):
            return False
        card = self.waste[-1]
        if not self._can_place_on_tableau(card, target_pile):
            return False

        self.waste.pop()
        self.tableau[target_pile].append(TableauCard(card=card, face_up=True))
        return True

    def move_tableau_to_tableau(self, source_pile: int, source_index: int, target_pile: int) -> bool:
        if source_pile == target_pile:
            return False
        if not self._valid_tableau_index(source_pile) or not self._valid_tableau_index(target_pile):
            return False

        source_cards = self.tableau[source_pile]
        if source_index < 0 or source_index >= len(source_cards):
            return False

        moving = source_cards[source_index:]
        if not moving or not moving[0].face_up:
            return False
        if not self._is_valid_tableau_sequence(moving):
            return False
        if not self._can_place_on_tableau(moving[0].card, target_pile):
            return False

        del source_cards[source_index:]
        self.tableau[target_pile].extend(moving)
        self._flip_tableau_top(source_pile)
        return True

    def _can_move_to_foundation(self, card: Card) -> bool:
        foundation = self.foundations[card.suit]
        if not foundation:
            return card.rank == 1
        return foundation[-1].rank + 1 == card.rank

    def _is_valid_tableau_sequence(self, entries: List[TableauCard]) -> bool:
        if not entries:
            return False
        for entry in entries:
            if not entry.face_up:
                return False
        for i in range(len(entries) - 1):
            upper = entries[i].card
            lower = entries[i + 1].card
            if upper.color == lower.color:
                return False
            if upper.rank != lower.rank + 1:
                return False
        return True

    def _can_place_on_tableau(self, card: Card, pile_index: int) -> bool:
        pile = self.tableau[pile_index]
        if not pile:
            return card.rank == 13

        top = pile[-1]
        if not top.face_up:
            return False
        return top.card.color != card.color and top.card.rank == card.rank + 1

    def _flip_tableau_top(self, pile_index: int) -> None:
        pile = self.tableau[pile_index]
        if pile and not pile[-1].face_up:
            pile[-1].face_up = True

    def _valid_tableau_index(self, index: int) -> bool:
        return 0 <= index < len(self.tableau)

    def total_cards(self) -> int:
        tableau_count = sum(len(pile) for pile in self.tableau)
        foundation_count = sum(len(pile) for pile in self.foundations.values())
        return len(self.stock) + len(self.waste) + tableau_count + foundation_count

    def is_won(self) -> bool:
        return all(len(pile) == 13 for pile in self.foundations.values())
