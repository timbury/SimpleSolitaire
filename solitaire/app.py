from __future__ import annotations

from pathlib import Path
import sys
from typing import Optional

from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from .engine import Card, KlondikeGame, SUITS

SUIT_FILE_CODES = {"♠": "S", "♥": "H", "♦": "D", "♣": "C"}
RANK_FILE_CODES = {1: "A", 11: "J", 12: "Q", 13: "K"}


class SolitaireApp(App):
    title = "FOSSolitaire"

    def build(self) -> BoxLayout:
        self.game = KlondikeGame()
        self.selected: Optional[dict] = None
        self.status_text = "Tap cards to select, then tap where to move them."

        self.project_root = self._resolve_project_root()
        self.assets_root = self.project_root / "assets"
        self.cards_front_root = self.assets_root / "cards" / "fronts"
        self.cards_back_root = self.assets_root / "cards" / "backs"
        self.ui_root = self.assets_root / "ui"

        self.card_back_image = self._resolve_card_back_image()
        self.table_background_image = self._resolve_table_background_image()

        root = BoxLayout(orientation="vertical", spacing=dp(8), padding=dp(8))
        self.root_layout = root
        self._table_image_rect: Optional[Rectangle] = None
        with root.canvas.before:
            self._table_color = Color(0.06, 0.38, 0.20, 1)
            self._table_rect = Rectangle(pos=root.pos, size=root.size)
            if self.table_background_image:
                self._table_image_rect = Rectangle(
                    source=self.table_background_image,
                    pos=root.pos,
                    size=root.size,
                )
        root.bind(pos=self._update_table_background, size=self._update_table_background)

        heading = Label(
            text="FOSSolitaire (Klondike, Draw 1)",
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

        self.top_row = GridLayout(cols=6, size_hint_y=None, height=dp(106), spacing=dp(6))
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

    def _resolve_project_root(self) -> Path:
        if hasattr(sys, "_MEIPASS"):
            return Path(getattr(sys, "_MEIPASS"))
        return Path(__file__).resolve().parent.parent

    def _resolve_card_back_image(self) -> Optional[str]:
        preferred = [
            "card_back.png",
            "back.png",
            "default.png",
            "classic_blue.png",
        ]
        for name in preferred:
            candidate = self.cards_back_root / name
            if candidate.is_file():
                return str(candidate)
        pngs = sorted(self.cards_back_root.glob("*.png"))
        if pngs:
            return str(pngs[0])
        return None

    def _resolve_table_background_image(self) -> Optional[str]:
        preferred = [
            "table_felt.png",
            "background.png",
            "felt.png",
        ]
        for name in preferred:
            candidate = self.ui_root / name
            if candidate.is_file():
                return str(candidate)
        pngs = sorted(self.ui_root.glob("*.png"))
        if pngs:
            return str(pngs[0])
        return None

    def _card_face_image(self, card: Card) -> Optional[str]:
        rank_code = RANK_FILE_CODES.get(card.rank, str(card.rank))
        suit_code = SUIT_FILE_CODES[card.suit]
        candidate = self.cards_front_root / f"{rank_code}{suit_code}.png"
        if candidate.is_file():
            return str(candidate)
        return None

    def _update_table_background(self, *_: object) -> None:
        self._table_rect.pos = self.root_layout.pos
        self._table_rect.size = self.root_layout.size
        if self._table_image_rect is not None:
            self._table_image_rect.pos = self.root_layout.pos
            self._table_image_rect.size = self.root_layout.size

    def _new_game(self) -> None:
        self.game.new_game()
        self.selected = None
        self.status_text = "New game started."
        self._refresh_ui()

    def _refresh_ui(self) -> None:
        self.top_row.clear_widgets()
        self.tableau_row.clear_widgets()

        stock_text = f"Stock\n{len(self.game.stock)}" if self.game.stock else "Recycle\nWaste"
        stock_button = self._make_button(
            stock_text,
            image_source=self.card_back_image if self.game.stock else None,
            size_hint_y=1.0,
            height=dp(102),
        )
        stock_button.bind(on_release=lambda *_: self._on_stock_pressed())
        self.top_row.add_widget(stock_button)

        waste_top = self.game.waste[-1].label if self.game.waste else "--"
        waste_selected = self.selected is not None and self.selected.get("kind") == "waste"
        waste_image = self._card_face_image(self.game.waste[-1]) if self.game.waste else None
        waste_button = self._make_button(
            "Waste" if waste_image else f"Waste\n{waste_top}",
            image_source=waste_image,
            selected=waste_selected,
            size_hint_y=1.0,
            height=dp(102),
        )
        waste_button.bind(on_release=lambda *_: self._on_waste_pressed())
        self.top_row.add_widget(waste_button)

        for suit in SUITS:
            top_card = self.game.foundations[suit][-1] if self.game.foundations[suit] else None
            top = top_card.label if top_card else "--"
            foundation_image = self._card_face_image(top_card) if top_card else None
            is_selected = (
                self.selected is not None
                and self.selected.get("kind") == "foundation"
                and self.selected.get("suit") == suit
            )
            foundation_button = self._make_button(
                suit if foundation_image else f"{suit}\n{top}",
                image_source=foundation_image,
                selected=is_selected,
                size_hint_y=1.0,
                height=dp(102),
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
                    card_image = self._card_face_image(entry.card) if entry.face_up else self.card_back_image
                    card_text = ""
                    if card_image is None:
                        card_text = entry.card.label if entry.face_up else "🂠"
                    card_button = self._make_button(
                        card_text,
                        image_source=card_image,
                        selected=selected,
                        size_hint_y=None,
                        height=dp(96),
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
        image_source: Optional[str] = None,
        selected: bool = False,
        size_hint_y: Optional[float] = None,
        height: float = dp(36),
    ) -> Button:
        button = Button(text=text, size_hint_y=size_hint_y, height=height)
        button.bold = True
        if image_source:
            button.background_normal = image_source
            button.background_down = image_source
            button.background_disabled_normal = image_source
            button.border = (0, 0, 0, 0)
            button.background_color = (0.76, 0.90, 1.0, 1) if selected else (1, 1, 1, 1)
            button.color = (0.08, 0.08, 0.08, 1)
        elif selected:
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
