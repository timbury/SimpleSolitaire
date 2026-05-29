import unittest

from solitaire.engine import Card, KlondikeGame, SUITS, TableauCard


class KlondikeIntegrationTests(unittest.TestCase):
    def _reset_minimal_state(self, game: KlondikeGame) -> None:
        game.stock = []
        game.waste = []
        game.foundations = {suit: [] for suit in SUITS}
        game.tableau = [[] for _ in range(7)]

    def test_draw_recycle_then_build_foundation_sequence(self) -> None:
        game = KlondikeGame(seed=13)
        self._reset_minimal_state(game)
        game.stock = [Card(2, "♠"), Card(1, "♠")]
        start_total = game.total_cards()

        self.assertTrue(game.draw_from_stock())
        self.assertEqual(game.waste[-1].label, "A♠")
        self.assertTrue(game.draw_from_stock())
        self.assertEqual(game.waste[-1].label, "2♠")

        # Cannot place a 2 on an empty foundation.
        self.assertFalse(game.move_waste_to_foundation("♠"))

        # Recycle waste back to stock, then draw in playable order.
        self.assertTrue(game.draw_from_stock())
        self.assertEqual(len(game.stock), 2)
        self.assertEqual(len(game.waste), 0)

        self.assertTrue(game.draw_from_stock())
        self.assertEqual(game.waste[-1].label, "A♠")
        self.assertTrue(game.move_waste_to_foundation("♠"))
        self.assertTrue(game.draw_from_stock())
        self.assertEqual(game.waste[-1].label, "2♠")
        self.assertTrue(game.move_waste_to_foundation("♠"))

        self.assertEqual([card.rank for card in game.foundations["♠"]], [1, 2])
        self.assertEqual(game.total_cards(), start_total)

    def test_tableau_stack_move_flips_hidden_card_then_moves_to_foundation(self) -> None:
        game = KlondikeGame(seed=17)
        self._reset_minimal_state(game)
        game.tableau[0] = [
            TableauCard(Card(1, "♣"), False),
            TableauCard(Card(6, "♥"), True),
            TableauCard(Card(5, "♣"), True),
        ]
        game.tableau[1] = [TableauCard(Card(7, "♠"), True)]
        start_total = game.total_cards()

        self.assertTrue(game.move_tableau_to_tableau(0, 1, 1))
        self.assertEqual([entry.card.label for entry in game.tableau[1]], ["7♠", "6♥", "5♣"])
        self.assertEqual(len(game.tableau[0]), 1)
        self.assertTrue(game.tableau[0][-1].face_up)
        self.assertEqual(game.tableau[0][-1].card.label, "A♣")

        self.assertTrue(game.move_tableau_to_foundation(0, "♣"))
        self.assertEqual([card.label for card in game.foundations["♣"]], ["A♣"])
        self.assertEqual(game.total_cards(), start_total)

    def test_foundation_to_tableau_roundtrip_sequence(self) -> None:
        game = KlondikeGame(seed=23)
        self._reset_minimal_state(game)
        game.foundations["♥"] = [Card(1, "♥"), Card(2, "♥")]
        game.tableau[2] = [TableauCard(Card(3, "♣"), True)]
        start_total = game.total_cards()

        self.assertTrue(game.move_foundation_to_tableau("♥", 2))
        self.assertEqual([entry.card.label for entry in game.tableau[2]], ["3♣", "2♥"])
        self.assertEqual([card.label for card in game.foundations["♥"]], ["A♥"])

        # Wrong suit target should fail even if rank would otherwise fit.
        self.assertFalse(game.move_tableau_to_foundation(2, "♠"))
        self.assertTrue(game.move_tableau_to_foundation(2, "♥"))
        self.assertEqual([card.label for card in game.foundations["♥"]], ["A♥", "2♥"])
        self.assertEqual([entry.card.label for entry in game.tableau[2]], ["3♣"])
        self.assertEqual(game.total_cards(), start_total)

    def test_invalid_tableau_sequence_with_face_down_middle_card_is_rejected(self) -> None:
        game = KlondikeGame(seed=29)
        self._reset_minimal_state(game)
        game.tableau[0] = [
            TableauCard(Card(8, "♣"), True),
            TableauCard(Card(7, "♥"), False),
            TableauCard(Card(6, "♣"), True),
        ]
        game.tableau[1] = [TableauCard(Card(9, "♦"), True)]
        start_total = game.total_cards()

        self.assertFalse(game.move_tableau_to_tableau(0, 0, 1))
        self.assertEqual([entry.card.label for entry in game.tableau[0]], ["8♣", "7♥", "6♣"])
        self.assertEqual([entry.face_up for entry in game.tableau[0]], [True, False, True])
        self.assertEqual([entry.card.label for entry in game.tableau[1]], ["9♦"])
        self.assertEqual(game.total_cards(), start_total)


if __name__ == "__main__":
    unittest.main()
