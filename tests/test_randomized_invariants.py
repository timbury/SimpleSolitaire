import random
import unittest
from typing import Callable, Dict, List, Tuple

from solitaire.engine import KlondikeGame, SUITS, TableauCard


CardTuple = Tuple[int, str]
Action = Callable[[], bool]


class KlondikeRandomizedInvariantTests(unittest.TestCase):
    def _snapshot(self, game: KlondikeGame) -> Dict[str, object]:
        return {
            "stock": [(card.rank, card.suit) for card in game.stock],
            "waste": [(card.rank, card.suit) for card in game.waste],
            "foundations": {
                suit: [(card.rank, card.suit) for card in pile]
                for suit, pile in game.foundations.items()
            },
            "tableau": [
                [(entry.card.rank, entry.card.suit, entry.face_up) for entry in pile]
                for pile in game.tableau
            ],
        }

    def _all_cards(self, game: KlondikeGame) -> List[CardTuple]:
        cards: List[CardTuple] = []
        cards.extend((card.rank, card.suit) for card in game.stock)
        cards.extend((card.rank, card.suit) for card in game.waste)
        for pile in game.foundations.values():
            cards.extend((card.rank, card.suit) for card in pile)
        for pile in game.tableau:
            cards.extend((entry.card.rank, entry.card.suit) for entry in pile)
        return cards

    def _assert_global_invariants(self, game: KlondikeGame) -> None:
        self.assertEqual(game.total_cards(), 52)
        all_cards = self._all_cards(game)
        self.assertEqual(len(all_cards), 52)
        self.assertEqual(len(set(all_cards)), 52)

        for suit, foundation in game.foundations.items():
            for expected_rank, card in enumerate(foundation, start=1):
                self.assertEqual(card.suit, suit)
                self.assertEqual(card.rank, expected_rank)

        for pile in game.tableau:
            if pile:
                self.assertTrue(pile[-1].face_up)

            face_up_started = False
            face_up_cards = []
            for entry in pile:
                self.assertIsInstance(entry, TableauCard)
                if entry.face_up:
                    face_up_started = True
                    face_up_cards.append(entry.card)
                else:
                    self.assertFalse(
                        face_up_started,
                        "Found a face-down card below an already face-up card.",
                    )

            for i in range(len(face_up_cards) - 1):
                upper = face_up_cards[i]
                lower = face_up_cards[i + 1]
                self.assertNotEqual(upper.color, lower.color)
                self.assertEqual(upper.rank, lower.rank + 1)

    def _available_actions(self, game: KlondikeGame) -> List[Action]:
        actions: List[Action] = [lambda: game.draw_from_stock()]

        if game.waste:
            actions.append(lambda: game.move_waste_to_foundation())
            for target in range(7):
                actions.append(lambda t=target: game.move_waste_to_tableau(t))

        for source in range(7):
            if game.tableau[source]:
                actions.append(lambda s=source: game.move_tableau_to_foundation(s))
            for index, entry in enumerate(game.tableau[source]):
                if not entry.face_up:
                    continue
                for target in range(7):
                    if source == target:
                        continue
                    actions.append(
                        lambda s=source, i=index, t=target: game.move_tableau_to_tableau(s, i, t)
                    )

        for suit in SUITS:
            if game.foundations[suit]:
                for target in range(7):
                    actions.append(lambda su=suit, t=target: game.move_foundation_to_tableau(su, t))

        return actions

    def test_randomized_action_stream_preserves_invariants(self) -> None:
        for run_seed in range(12):
            rng = random.Random(run_seed)
            game = KlondikeGame(seed=1000 + run_seed)
            self._assert_global_invariants(game)

            for _ in range(350):
                if rng.random() < 0.15:
                    before = self._snapshot(game)
                    self.assertFalse(game.move_tableau_to_tableau(0, 0, 0))
                    self.assertEqual(before, self._snapshot(game))
                else:
                    action = rng.choice(self._available_actions(game))
                    action()
                self._assert_global_invariants(game)

    def test_randomized_wrong_suit_foundation_attempts_do_not_mutate_state(self) -> None:
        for run_seed in range(6):
            rng = random.Random(500 + run_seed)
            game = KlondikeGame(seed=2000 + run_seed)
            self._assert_global_invariants(game)

            for _ in range(200):
                if not game.waste:
                    game.draw_from_stock()

                if game.waste:
                    wrong_suits = [suit for suit in SUITS if suit != game.waste[-1].suit]
                    before = self._snapshot(game)
                    self.assertFalse(game.move_waste_to_foundation(rng.choice(wrong_suits)))
                    self.assertEqual(before, self._snapshot(game))

                action = rng.choice(self._available_actions(game))
                action()
                self._assert_global_invariants(game)


if __name__ == "__main__":
    unittest.main()
