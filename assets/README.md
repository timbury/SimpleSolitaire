# Artwork asset structure
Drop your artwork files into these folders:

- `assets/cards/fronts/` for all 52 face images named like:
  - `AS.png`, `2S.png`, `3S.png`, ..., `10S.png`, `JS.png`, `QS.png`, `KS.png`
  - Same format for hearts (`H`), diamonds (`D`), clubs (`C`)
- `assets/cards/backs/` for card back images
  - Preferred names checked first: `card_back.png`, `back.png`, `default.png`, `classic_blue.png`
- `assets/ui/` for background images
  - Preferred names checked first: `table_felt.png`, `background.png`, `felt.png`

If a requested image is missing, the app falls back to text rendering automatically.
