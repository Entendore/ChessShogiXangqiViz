import os
import re
import argparse

# ----------------------------
# Layouts
# ----------------------------
LAYOUTS = {
    "default": {"piece_size": 80, "margin": 15, "cols": 10, "label_height": 20},
    "compact": {"piece_size": 50, "margin": 8, "cols": 12, "label_height": 15},
    "poster": {"piece_size": 120, "margin": 25, "cols": 8, "label_height": 30}
}

# ----------------------------
# Themes
# ----------------------------
themes = {
    "classic": {
        "base_colors": {"red": "#ff0000", "black": "#000000"},
        "text_colors": {"red": "#aa0000", "black": "#555555"},
        "border_colors": {"red": "#880000", "black": "#222222"},
        "promotion_highlight": "#fff0b3"
    },
    "pastel": {
        "base_colors": {"red": "#ffcccc", "black": "#808080"},
        "text_colors": {"red": "#cc6666", "black": "#444444"},
        "border_colors": {"red": "#cc4444", "black": "#222222"},
        "promotion_highlight": "#ffe5b3"
    },
    "dark_mode": {
        "base_colors": {"red": "#880000", "black": "#222222"},
        "text_colors": {"red": "#ff6666", "black": "#aaaaaa"},
        "border_colors": {"red": "#ff4444", "black": "#aaaaaa"},
        "promotion_highlight": "#ffcc88"
    }
}

# ----------------------------
# Xiangqi pieces
# ----------------------------
pieces = {
    "General": "將", "Advisor": "士", "Elephant": "象", "Horse": "馬",
    "Chariot": "車", "Cannon": "砲", "Soldier": "卒"
}

# ----------------------------
# SVG creation
# ----------------------------
def create_xiangqi_svg(symbol, fill_color, text_color, border_color, size=100):
    font_size = size / max(1.8, len(symbol) * 0.9)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}">
  <circle cx="{size/2}" cy="{size/2}" r="{size/2 - 5}" fill="{fill_color}" stroke="{border_color}" stroke-width="4"/>
  <text x="50%" y="55%" font-size="{font_size}" text-anchor="middle" fill="{text_color}" font-family="SimSun, Arial" dominant-baseline="middle">{symbol}</text>
</svg>'''

# ----------------------------
# Preview generator
# ----------------------------
def generate_preview(piece_svgs, preview_file, text_colors, piece_size, margin, cols, label_height):
    rows = (len(piece_svgs) + cols - 1) // cols
    width = cols * (piece_size + margin) + margin
    height = rows * (piece_size + margin + label_height) + margin
    svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">\n'
    x, y = margin, margin

    for idx, (svg_str, piece_name, player) in enumerate(piece_svgs):
        inner_svg = svg_str.split(">", 1)[1].rsplit("</svg>", 1)[0]
        text_color = text_colors[player]
        inner_svg = re.sub(r'(<text[^>]*?)fill="[^"]+"', rf'\1fill="{text_color}"', inner_svg)
        svg_content += f'<g transform="translate({x},{y})">{inner_svg}</g>\n'
        svg_content += f'<text x="{x + piece_size/2}" y="{y + piece_size + label_height*0.7}" text-anchor="middle" font-family="Arial" font-size="12" fill="black">{piece_name}</text>\n'
        x += piece_size + margin
        if (idx + 1) % cols == 0:
            x = margin
            y += piece_size + margin + label_height

    svg_content += '</svg>'
    with open(preview_file, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Preview sheet generated: {preview_file}")

# ----------------------------
# CLI
# ----------------------------
parser = argparse.ArgumentParser(description="Generate Xiangqi pieces SVGs with themes.")
parser.add_argument("--theme", type=str, default="classic", choices=themes.keys())
parser.add_argument("--layout", type=str, default="default", choices=LAYOUTS.keys())
parser.add_argument("--output", type=str, default="xiangqi_svgs")
parser.add_argument("--batch", action="store_true")
for player in ["red","black"]:
    for key_type in ["fill","text","border"]:
        parser.add_argument(f"--xiangqi-{player}-{key_type}", type=str, help=f"Override {key_type} color for {player} pieces")
args = parser.parse_args()

# ----------------------------
# Generation loop
# ----------------------------
themes_to_generate = themes.keys() if args.batch else [args.theme]
layouts_to_generate = LAYOUTS.keys() if args.batch else [args.layout]

for theme_name in themes_to_generate:
    theme_data = themes[theme_name]
    base_colors = theme_data["base_colors"].copy()
    text_colors = theme_data["text_colors"].copy()
    border_colors = theme_data["border_colors"].copy()

    for player in ["red","black"]:
        for key_type in ["fill","text","border"]:
            cli_value = getattr(args, f"xiangqi_{player}_{key_type}")
            if cli_value:
                if key_type == "fill": base_colors[player] = cli_value
                elif key_type == "text": text_colors[player] = cli_value
                elif key_type == "border": border_colors[player] = cli_value

    for layout_name in layouts_to_generate:
        layout = LAYOUTS[layout_name]
        piece_size = layout["piece_size"]
        margin = layout["margin"]
        cols = layout["cols"]
        label_height = layout["label_height"]

        print(f"\nGenerating Xiangqi theme '{theme_name}' with layout '{layout_name}'")
        theme_dir = os.path.join(args.output, f"{theme_name}_{layout_name}")
        os.makedirs(theme_dir, exist_ok=True)

        piece_svgs_combined = []
        for piece_name, symbol in pieces.items():
            for player in ["red","black"]:
                svg_str = create_xiangqi_svg(symbol, base_colors[player], text_colors[player], border_colors[player], piece_size)
                path_svg = os.path.join(theme_dir, f"{piece_name}_{player}.svg")
                with open(path_svg, "w", encoding="utf-8") as f:
                    f.write(svg_str)
                piece_svgs_combined.append((svg_str, piece_name, player))

        preview_svg = os.path.join(theme_dir, "preview_sheet_labeled.svg")
        generate_preview(piece_svgs_combined, preview_svg, text_colors, piece_size, margin, cols, label_height)
