import unittest

from solitaire.engine import Card, KlondikeGame, SUITS, TableauCard


class KlondikeGameTests(unittest.TestCase):
    def test_initial_deal_has_expected_layout(self) -> None:
        game = KlondikeGame(seed=7)
        self.assertEqual(game.total_cards(), 52)
        self.assertEqual([len(pile) for pile in game.tableau], [1, 2, 3, 4, 5, 6, 7])
        for pile in game.tableau:
            self.assertTrue(pile[-1].face_up)
            for card in pile[:-1]:
                self.assertFalse(card.face_up)

    def test_move_waste_ace_to_foundation(self) -> None:
        game = KlondikeGame(seed=1)
        game.stock = []
        game.waste = [Card(1, "♠")]
        game.foundations = {suit: [] for suit in SUITS}
        self.assertTrue(game.move_waste_to_foundation("♠"))
        self.assertEqual(len(game.waste), 0)
        self.assertEqual(game.foundations["♠"][-1].rank, 1)

    def test_only_king_can_move_to_empty_tableau(self) -> None:
        game = KlondikeGame(seed=1)
        game.tableau = [[] for _ in range(7)]
        game.waste = [Card(12, "♣")]
        self.assertFalse(game.move_waste_to_tableau(0))
        game.waste = [Card(13, "♣")]
        self.assertTrue(game.move_waste_to_tableau(0))

    def test_move_valid_tableau_stack(self) -> None:
        game = KlondikeGame(seed=1)
        game.tableau = [
            [TableauCard(Card(5, "♣"), True), TableauCard(Card(4, "♥"), True)],
            [TableauCard(Card(6, "♦"), True)],
            [],
            [],
            [],
            [],
            [],
        ]
        self.assertTrue(game.move_tableau_to_tableau(0, 0, 1))
        self.assertEqual(len(game.tableau[0]), 0)
        self.assertEqual([entry.card.label for entry in game.tableau[1]], ["6♦", "5♣", "4♥"])

    def test_win_detection(self) -> None:
        game = KlondikeGame(seed=2)
        game.foundations = {
            suit: [Card(rank, suit) for rank in range(1, 14)]
            for suit in SUITS
        }
        self.assertTrue(game.is_won())


if __name__ == "__main__":
    unittest.main()
