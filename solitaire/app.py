from __future__ import annotations

from typing import Optional

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from .engine import KlondikeGame, SUITS


class SolitaireApp(App):
    title = "Simple Solitaire"

    def build(self) -> BoxLayout:
        self.game = KlondikeGame()
        self.selected: Optional[dict] = None
        self.status_text = "Tap cards to select, then tap where to move them."

        root = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))

        heading = Label(
            text="Simple Solitaire (Klondike, Draw 1)",
            size_hint_y=None,
            height=dp(30),
            bold=True,
        )
        root.add_widget(heading)

        controls = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        new_game_button = Button(text="New Game")
        new_game_button.bind(on_release=lambda *_: self._new_game())
        controls.add_widget(new_game_button)
        root.add_widget(controls)

        self.top_row = GridLayout(cols=6, size_hint_y=None, height=dp(74), spacing=dp(6))
        root.add_widget(self.top_row)

        self.tableau_row = GridLayout(cols=7, spacing=dp(6))
        root.add_widget(self.tableau_row)

        self.status_label = Label(
            text=self.status_text,
            size_hint_y=None,
            height=dp(30),
        )
        root.add_widget(self.status_label)

        self._refresh_ui()
        return root

    def _new_game(self) -> None:
        self.game.new_game()
        self.selected = None
        self.status_text = "New game started."
        self._refresh_ui()

    def _refresh_ui(self) -> None:
        self.top_row.clear_widgets()
        self.tableau_row.clear_widgets()

        stock_text = f"Stock\n{len(self.game.stock)}" if self.game.stock else "Recycle\nWaste"
        stock_button = self._make_button(stock_text, size_hint_y=1.0, height=dp(72))
        stock_button.bind(on_release=lambda *_: self._on_stock_pressed())
        self.top_row.add_widget(stock_button)

        waste_top = self.game.waste[-1].label if self.game.waste else "--"
        waste_selected = self.selected is not None and self.selected.get("kind") == "waste"
        waste_button = self._make_button(
            f"Waste\n{waste_top}",
            selected=waste_selected,
            size_hint_y=1.0,
            height=dp(72),
        )
        waste_button.bind(on_release=lambda *_: self._on_waste_pressed())
        self.top_row.add_widget(waste_button)

        for suit in SUITS:
            top = self.game.foundations[suit][-1].label if self.game.foundations[suit] else "--"
            is_selected = (
                self.selected is not None
                and self.selected.get("kind") == "foundation"
                and self.selected.get("suit") == suit
            )
            foundation_button = self._make_button(
                f"{suit}\n{top}",
                selected=is_selected,
                size_hint_y=1.0,
                height=dp(72),
            )
            foundation_button.bind(on_release=lambda *_x, picked_suit=suit: self._on_foundation_pressed(picked_suit))
            self.top_row.add_widget(foundation_button)

        for pile_index, pile in enumerate(self.game.tableau):
            column = BoxLayout(orientation="vertical", spacing=dp(2))

            destination_button = self._make_button(
                f"T{pile_index + 1}",
                size_hint_y=None,
                height=dp(28),
            )
            destination_button.bind(
                on_release=lambda *_x, idx=pile_index: self._on_tableau_destination_pressed(idx)
            )
            column.add_widget(destination_button)

            if not pile:
                empty_button = self._make_button(
                    "Empty\n(K only)",
                    size_hint_y=None,
                    height=dp(44),
                )
                empty_button.bind(
                    on_release=lambda *_x, idx=pile_index: self._on_tableau_destination_pressed(idx)
                )
                column.add_widget(empty_button)
            else:
                for card_index, entry in enumerate(pile):
                    selected = (
                        self.selected is not None
                        and self.selected.get("kind") == "tableau"
                        and self.selected.get("pile") == pile_index
                        and self.selected.get("index") == card_index
                    )
                    card_text = entry.card.label if entry.face_up else "🂠"
                    card_button = self._make_button(
                        card_text,
                        selected=selected,
                        size_hint_y=None,
                        height=dp(36),
                    )
                    card_button.bind(
                        on_release=lambda *_x, p=pile_index, c=card_index: self._on_tableau_card_pressed(p, c)
                    )
                    column.add_widget(card_button)

            self.tableau_row.add_widget(column)

        self.status_label.text = self.status_text

    def _make_button(
        self,
        text: str,
        *,
        selected: bool = False,
        size_hint_y: Optional[float] = None,
        height: float = dp(36),
    ) -> Button:
        button = Button(text=text, size_hint_y=size_hint_y, height=height)
        if selected:
            button.background_normal = ""
            button.background_color = (0.25, 0.55, 0.95, 1)
        return button

    def _on_stock_pressed(self) -> None:
        self.selected = None
        moved = self.game.draw_from_stock()
        if moved:
            self.status_text = "Drew from stock (or recycled waste when stock was empty)."
        else:
            self.status_text = "No cards left to draw."
        self._refresh_ui()

    def _on_waste_pressed(self) -> None:
        if not self.game.waste:
            self.status_text = "Waste pile is empty."
        elif self.selected and self.selected.get("kind") == "waste":
            self.selected = None
            self.status_text = "Selection cleared."
        else:
            self.selected = {"kind": "waste"}
            self.status_text = "Selected waste card."
        self._refresh_ui()

    def _on_foundation_pressed(self, suit: str) -> None:
        if self.selected is None:
            if self.game.foundations[suit]:
                self.selected = {"kind": "foundation", "suit": suit}
                self.status_text = f"Selected {suit} foundation card."
            else:
                self.status_text = "That foundation pile is empty."
            self._refresh_ui()
            return

        if self.selected.get("kind") == "foundation" and self.selected.get("suit") == suit:
            self.selected = None
            self.status_text = "Selection cleared."
            self._refresh_ui()
            return

        moved = False
        kind = self.selected.get("kind")
        if kind == "waste":
            moved = self.game.move_waste_to_foundation(suit)
        elif kind == "tableau":
            moved = self.game.move_tableau_to_foundation(int(self.selected["pile"]), suit)

        if moved:
            self.selected = None
            self.status_text = f"Moved card to {suit} foundation."
            if self.game.is_won():
                self.status_text = "You won! Start a new game to play again."
        else:
            self.status_text = "That move is not legal."

        self._refresh_ui()

    def _on_tableau_card_pressed(self, pile_index: int, card_index: int) -> None:
        entry = self.game.tableau[pile_index][card_index]
        if not entry.face_up:
            self.status_text = "Face-down cards cannot be moved."
            self._refresh_ui()
            return

        if self.selected is None:
            self.selected = {"kind": "tableau", "pile": pile_index, "index": card_index}
            self.status_text = f"Selected tableau pile {pile_index + 1}."
            self._refresh_ui()
            return

        if (
            self.selected.get("kind") == "tableau"
            and self.selected.get("pile") == pile_index
            and self.selected.get("index") == card_index
        ):
            self.selected = None
            self.status_text = "Selection cleared."
            self._refresh_ui()
            return

        moved = self._move_selected_to_tableau(pile_index)
        if not moved:
            self.selected = {"kind": "tableau", "pile": pile_index, "index": card_index}
            self.status_text = f"Selected tableau pile {pile_index + 1}."
        self._refresh_ui()

    def _on_tableau_destination_pressed(self, pile_index: int) -> None:
        if self.selected is None:
            self.status_text = "Select a source card first."
            self._refresh_ui()
            return

        moved = self._move_selected_to_tableau(pile_index)
        if moved:
            self.selected = None
            if self.game.is_won():
                self.status_text = "You won! Start a new game to play again."
        self._refresh_ui()

    def _move_selected_to_tableau(self, destination: int) -> bool:
        moved = False
        kind = self.selected.get("kind")
        if kind == "waste":
            moved = self.game.move_waste_to_tableau(destination)
        elif kind == "tableau":
            moved = self.game.move_tableau_to_tableau(
                int(self.selected["pile"]),
                int(self.selected["index"]),
                destination,
            )
        elif kind == "foundation":
            moved = self.game.move_foundation_to_tableau(
                str(self.selected["suit"]),
                destination,
            )

        if moved:
            self.status_text = f"Moved card(s) to tableau {destination + 1}."
        else:
            self.status_text = "That move is not legal."
        return moved
