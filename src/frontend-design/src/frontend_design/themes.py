"""
Reusable theme definitions for presentations, documents, and interfaces.

Each theme provides:
- Color palette (background, surface, primary, accent, text colors)
- Font pairings (heading, body)
- Aesthetic description
- CSS for Marp presentations
"""

# ======================================================
# Theme Definitions
# ======================================================

THEMES = {
    "noir": {
        "name": "Noir",
        "description": "Dramatic high-contrast dark theme with editorial typography. Bold, cinematic feel.",
        "aesthetic": "Editorial/Magazine meets Film Noir",
        "colors": {
            "background": "#0A0A0A",
            "surface": "#141414",
            "primary": "#1A1A1A",
            "accent": "#FF3B3B",
            "text": "#E8E8E8",
            "text_muted": "#6B6B6B",
            "heading": "#FFFFFF",
        },
        "fonts": {
            "heading": "Georgia",
            "body": "Verdana",
        },
        "marp_css": """
/* @theme noir */
@import 'default';

section {
  background: #0a0a0a;
  color: #e8e8e8;
  font-family: 'Verdana', sans-serif;
  font-size: 28px;
  padding: 60px 80px;
}

h1 {
  font-family: 'Georgia', serif;
  font-size: 3.2em;
  font-weight: 700;
  color: #ffffff;
  border-bottom: 4px solid #ff3b3b;
  padding-bottom: 0.3em;
  display: inline-block;
}

h2 {
  font-family: 'Georgia', serif;
  font-size: 2.2em;
  color: #ffffff;
}

h3 {
  font-size: 1.4em;
  color: #ff3b3b;
  text-transform: uppercase;
  letter-spacing: 0.15em;
}

li::marker { color: #ff3b3b; }
strong { color: #ffffff; }
em { color: #ff3b3b; font-style: normal; }
code { background: #141414; color: #ff3b3b; padding: 0.2em 0.5em; }

blockquote {
  border-left: 4px solid #ff3b3b;
  padding-left: 1.5em;
  color: #6b6b6b;
  font-style: italic;
}

section.lead {
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
}

section.lead h1 { font-size: 4em; border-bottom: none; }
section.lead p { color: #6b6b6b; font-size: 1.4em; }

section.invert {
  background: #ff3b3b;
  color: #0a0a0a;
}
section.invert h1, section.invert h2 { color: #0a0a0a; border-bottom-color: #0a0a0a; }

th { background: #141414; color: #ff3b3b; }
td { border-bottom: 1px solid #141414; }
""",
    },
    "brutalist": {
        "name": "Brutalist",
        "description": "Raw, bold design with sharp geometry. No-nonsense, impactful presentations.",
        "aesthetic": "Brutalist/Industrial with Swiss typography",
        "colors": {
            "background": "#F5F5F0",
            "surface": "#FFFFFF",
            "primary": "#1A1A1A",
            "accent": "#0000FF",
            "secondary": "#FF0000",
            "text": "#1A1A1A",
            "text_muted": "#666666",
            "heading": "#1A1A1A",
        },
        "fonts": {
            "heading": "Impact",
            "body": "Arial",
        },
        "marp_css": """
/* @theme brutalist */
@import 'default';

section {
  background: #f5f5f0;
  color: #1a1a1a;
  font-family: 'Arial', sans-serif;
  font-size: 26px;
  padding: 50px 70px;
  border: 8px solid #1a1a1a;
}

h1 {
  font-family: 'Impact', sans-serif;
  font-size: 3.5em;
  text-transform: uppercase;
  letter-spacing: -0.03em;
}
h1::after {
  content: '';
  display: block;
  width: 100px;
  height: 12px;
  background: #0000ff;
  margin-top: 0.3em;
}

h2 {
  font-family: 'Impact', sans-serif;
  font-size: 2em;
  text-transform: uppercase;
  color: #0000ff;
}

h3 {
  border-left: 6px solid #ff0000;
  padding-left: 0.8em;
  text-transform: uppercase;
}

ul { list-style: none; padding-left: 0; }
ul li { padding-left: 1.8em; position: relative; }
ul li::before { content: '→'; position: absolute; left: 0; color: #0000ff; }

strong { background: #0000ff; color: #ffffff; padding: 0 0.3em; }
em { border-bottom: 3px solid #ff0000; font-style: normal; }
code { background: #1a1a1a; color: #f5f5f0; }

blockquote {
  background: #1a1a1a;
  color: #f5f5f0;
  padding: 1.5em 2em;
}

section.lead {
  background: #1a1a1a;
  color: #f5f5f0;
  border-color: #1a1a1a;
}
section.lead h1 { color: #f5f5f0; }
section.lead h1::after { background: #ff0000; }

section.invert {
  background: #0000ff;
  color: #ffffff;
  border-color: #0000ff;
}

th { background: #1a1a1a; color: #f5f5f0; text-transform: uppercase; }
td { border: 2px solid #1a1a1a; }
""",
    },
    "organic": {
        "name": "Organic",
        "description": "Warm, natural palette with gentle curves. Perfect for wellness, sustainability, lifestyle.",
        "aesthetic": "Natural/Earthy with soft, approachable typography",
        "colors": {
            "background": "#FDFBF7",
            "surface": "#F5F0E8",
            "primary": "#166534",
            "accent": "#B8860B",
            "secondary": "#6B8E6B",
            "text": "#2D3A2D",
            "text_muted": "#57534E",
            "heading": "#14532D",
        },
        "fonts": {
            "heading": "Georgia",
            "body": "Verdana",
        },
        "marp_css": """
/* @theme organic */
@import 'default';

section {
  background: #fdfbf7;
  background-image:
    radial-gradient(ellipse at 20% 80%, rgba(107, 142, 107, 0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(184, 134, 11, 0.06) 0%, transparent 50%);
  color: #2d3a2d;
  font-family: 'Verdana', sans-serif;
  font-size: 26px;
  padding: 60px 80px;
}

h1 {
  font-family: 'Georgia', serif;
  font-size: 2.8em;
  font-weight: 400;
  position: relative;
  padding-bottom: 0.4em;
}
h1::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, #b8860b 0%, #6b8e6b 100%);
}

h2 { font-family: 'Georgia', serif; color: #6b8e6b; font-weight: 400; }
h3 { color: #b8860b; }

ul li::marker { color: #6b8e6b; }
strong { color: #b8860b; }
em { color: #6b8e6b; }
code { background: #f5f0e8; border-radius: 20px; border: 1px solid rgba(45, 58, 45, 0.15); }

blockquote {
  background: #f5f0e8;
  border-left: 4px solid #6b8e6b;
  border-radius: 0 12px 12px 0;
  font-style: italic;
}

section.lead {
  text-align: center;
  background:
    radial-gradient(ellipse at 50% 50%, rgba(107, 142, 107, 0.12) 0%, transparent 70%),
    #fdfbf7;
}
section.lead h1::after { left: 50%; transform: translateX(-50%); }

section.invert { background: #6b8e6b; color: #ffffff; }
section.invert h1, section.invert h2 { color: #ffffff; }

th { background: #6b8e6b; color: #ffffff; }
td { background: #f5f0e8; border-bottom: 1px solid rgba(45, 58, 45, 0.1); }
img { border-radius: 12px; box-shadow: 0 8px 24px rgba(45, 58, 45, 0.12); }
""",
    },
    "neon": {
        "name": "Neon",
        "description": "Electric, vibrant dark theme with glowing accents. Tech-forward and energetic.",
        "aesthetic": "Cyberpunk/Retro-futuristic with bold neon highlights",
        "colors": {
            "background": "#0D0D1A",
            "surface": "#161625",
            "primary": "#4C1D95",
            "accent": "#00FFCC",
            "secondary": "#FF00AA",
            "tertiary": "#FFCC00",
            "text": "#E0E0FF",
            "text_muted": "#94A3B8",
            "heading": "#FFFFFF",
        },
        "fonts": {
            "heading": "Impact",
            "body": "Trebuchet MS",
        },
        "marp_css": """
/* @theme neon */
@import 'default';

section {
  background: #0d0d1a;
  background-image:
    linear-gradient(180deg, rgba(0, 255, 204, 0.03) 0%, transparent 50%),
    linear-gradient(0deg, rgba(255, 0, 170, 0.03) 0%, transparent 50%);
  color: #e0e0ff;
  font-family: 'Trebuchet MS', sans-serif;
  font-size: 26px;
  padding: 50px 70px;
}

h1 {
  font-family: 'Impact', sans-serif;
  font-size: 3.2em;
  color: #ffffff;
  text-transform: uppercase;
  text-shadow: 0 0 10px #00ffcc, 0 0 30px rgba(0, 255, 204, 0.5);
}

h2 {
  font-family: 'Impact', sans-serif;
  font-size: 2em;
  color: #ff00aa;
  text-transform: uppercase;
  text-shadow: 0 0 15px rgba(255, 0, 170, 0.6);
}

h3 { color: #ffcc00; text-transform: uppercase; letter-spacing: 0.15em; }

ul { list-style: none; padding-left: 0; }
ul li { padding-left: 2em; position: relative; }
ul li::before { content: '▸'; position: absolute; left: 0; color: #00ffcc; text-shadow: 0 0 8px #00ffcc; }

strong { color: #00ffcc; text-shadow: 0 0 8px rgba(0, 255, 204, 0.5); }
em { color: #ff00aa; font-style: normal; }
code { background: #161625; color: #00ffcc; border: 1px solid #00ffcc; box-shadow: 0 0 8px rgba(0, 255, 204, 0.3); }

blockquote {
  border-left: 3px solid #ff00aa;
  box-shadow: inset 4px 0 15px rgba(255, 0, 170, 0.2);
}

section.lead {
  text-align: center;
  background:
    radial-gradient(ellipse at 30% 70%, rgba(255, 0, 170, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 70% 30%, rgba(0, 255, 204, 0.15) 0%, transparent 50%),
    #0d0d1a;
}
section.lead h1 {
  font-size: 4em;
  text-shadow: 0 0 20px #00ffcc, 0 0 40px rgba(0, 255, 204, 0.6);
}

section.invert {
  background: linear-gradient(135deg, #ff00aa 0%, #aa0066 100%);
  color: #ffffff;
}
section.invert h1, section.invert h2 { color: #ffffff; text-shadow: 0 0 20px rgba(255, 255, 255, 0.5); }

th { background: #161625; color: #00ffcc; border-bottom: 2px solid #00ffcc; }
td { border-bottom: 1px solid rgba(0, 255, 204, 0.3); }
a { color: #00ffcc; text-shadow: 0 0 8px rgba(0, 255, 204, 0.5); }
""",
    },
    "minimal": {
        "name": "Minimal",
        "description": "Ultra-clean, refined design with precise typography. Content takes center stage.",
        "aesthetic": "Swiss/Minimalist with intentional whitespace",
        "colors": {
            "background": "#FFFFFF",
            "surface": "#FAFAFA",
            "primary": "#0066CC",
            "accent": "#0066CC",
            "text": "#1A1A1A",
            "text_muted": "#888888",
            "heading": "#1A1A1A",
        },
        "fonts": {
            "heading": "Georgia",
            "body": "Arial",
        },
        "marp_css": """
/* @theme minimal */
@import 'default';

section {
  background: #ffffff;
  color: #1a1a1a;
  font-family: 'Arial', sans-serif;
  font-size: 26px;
  padding: 80px 100px;
}

h1 {
  font-family: 'Georgia', serif;
  font-size: 2.6em;
  font-weight: 400;
  letter-spacing: -0.02em;
}

h2 { font-family: 'Georgia', serif; font-size: 1.8em; font-weight: 400; }

h3 {
  font-size: 0.9em;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: #888888;
}

ul li::marker { color: #0066cc; }
code { background: #fafafa; font-size: 0.9em; }

blockquote {
  border-left: 2px solid #0066cc;
  color: #888888;
  font-style: italic;
}

section.lead {
  padding-left: 120px;
}
section.lead h1 { font-size: 3.2em; max-width: 80%; }
section.lead p { color: #888888; max-width: 60%; }

section.invert {
  background: #1a1a1a;
  color: #ffffff;
}
section.invert h1, section.invert h2, section.invert p { color: #ffffff; }
section.invert h3 { color: #888888; }

th {
  color: #888888;
  font-size: 0.85em;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  border-bottom: 2px solid #1a1a1a;
  background: transparent;
}
td { border-bottom: 1px solid #fafafa; }
a { color: #0066cc; }
""",
    },
    "retro": {
        "name": "Retro",
        "description": "Nostalgic 70s/80s vibes with warm tones and geometric flair. Fun and distinctive.",
        "aesthetic": "Retro/Vintage with bold geometric patterns",
        "colors": {
            "background": "#FFF8E7",
            "surface": "#FFE4B5",
            "primary": "#E85D04",
            "accent": "#E85D04",
            "secondary": "#6A4C93",
            "tertiary": "#1982C4",
            "text": "#2D1810",
            "text_muted": "#78716C",
            "heading": "#E85D04",
        },
        "fonts": {
            "heading": "Impact",
            "body": "Trebuchet MS",
        },
        "marp_css": """
/* @theme retro */
@import 'default';

section {
  background: #fff8e7;
  background-image:
    linear-gradient(135deg, transparent 40%, rgba(232, 93, 4, 0.05) 40%, rgba(232, 93, 4, 0.05) 60%, transparent 60%);
  color: #2d1810;
  font-family: 'Trebuchet MS', sans-serif;
  font-size: 26px;
  padding: 50px 70px;
}

h1 {
  font-family: 'Impact', sans-serif;
  font-size: 3em;
  color: #e85d04;
  text-transform: uppercase;
  display: inline-block;
  position: relative;
}
h1::before {
  content: '';
  position: absolute;
  bottom: -8px;
  left: 0;
  right: 0;
  height: 8px;
  background: repeating-linear-gradient(90deg, #e85d04 0px, #e85d04 20px, #6a4c93 20px, #6a4c93 40px);
}

h2 {
  font-family: 'Impact', sans-serif;
  font-size: 2em;
  color: #6a4c93;
  text-transform: uppercase;
}

h3 { color: #1982c4; text-transform: uppercase; letter-spacing: 0.1em; }

ul { list-style: none; padding-left: 0; }
ul li { padding-left: 2em; position: relative; }
ul li::before { content: '★'; position: absolute; left: 0; color: #e85d04; }

strong { background: #e85d04; color: #ffffff; padding: 0.1em 0.4em; }
em { color: #6a4c93; font-weight: 600; }
code { background: #2d1810; color: #fff8e7; }

blockquote {
  background: #ffe4b5;
  border-left: 8px solid #6a4c93;
  position: relative;
}
blockquote::before { content: '"'; font-size: 4em; position: absolute; top: -0.2em; left: 0.2em; color: #e85d04; opacity: 0.5; }

section.lead {
  text-align: center;
  background-size: 100% 8px;
  background-repeat: no-repeat;
  background-position: bottom;
  background-image: linear-gradient(45deg, #e85d04 0%, #e85d04 33%, #6a4c93 33%, #6a4c93 66%, #1982c4 66%, #1982c4 100%);
}
section.lead h1 { color: #2d1810; }
section.lead h1::before { display: none; }

section.invert { background: #6a4c93; color: #ffffff; background-image: none; }
section.invert h1, section.invert h2 { color: #ffffff; }
section.invert h1::before { background: repeating-linear-gradient(90deg, #ffffff 0px, #ffffff 20px, #e85d04 20px, #e85d04 40px); }

th { background: #e85d04; color: #ffffff; text-transform: uppercase; }
td { border: 2px solid #2d1810; background: #fff8e7; }
tr:nth-child(even) td { background: #ffe4b5; }
a { color: #1982c4; text-decoration: underline; text-decoration-thickness: 2px; }
""",
    },
}


# ======================================================
# Color Palettes (for non-Marp use)
# ======================================================

PALETTES = {
    "classic_blue": {
        "name": "Classic Blue",
        "colors": ["#1C2833", "#2E4053", "#AAB7B8", "#F4F6F6"],
        "description": "Traditional professional palette",
    },
    "teal_coral": {
        "name": "Teal & Coral",
        "colors": ["#5EA8A7", "#277884", "#FE4447", "#FFFFFF"],
        "description": "Vibrant, modern contrast",
    },
    "bold_red": {
        "name": "Bold Red",
        "colors": ["#C0392B", "#E74C3C", "#F39C12", "#F1C40F", "#2ECC71"],
        "description": "Energetic, attention-grabbing",
    },
    "burgundy_luxury": {
        "name": "Burgundy Luxury",
        "colors": ["#5D1D2E", "#951233", "#C15937", "#997929"],
        "description": "Sophisticated, premium feel",
    },
    "deep_purple_emerald": {
        "name": "Deep Purple & Emerald",
        "colors": ["#B165FB", "#181B24", "#40695B", "#FFFFFF"],
        "description": "Modern tech aesthetic",
    },
    "sage_terracotta": {
        "name": "Sage & Terracotta",
        "colors": ["#87A96B", "#E07A5F", "#F4F1DE", "#2C2C2C"],
        "description": "Earthy, organic warmth",
    },
    "monochrome": {
        "name": "Monochrome",
        "colors": ["#000000", "#333333", "#666666", "#999999", "#FFFFFF"],
        "description": "Classic black and white",
    },
    "ocean_depths": {
        "name": "Ocean Depths",
        "colors": ["#0A1628", "#1E3A5F", "#3D5A80", "#98C1D9", "#E0FBFC"],
        "description": "Deep, calming blues",
    },
}


# ======================================================
# Helper Functions
# ======================================================


def get_theme(name: str) -> dict | None:
    """Get a theme by name."""
    return THEMES.get(name)


def get_theme_css(name: str) -> str | None:
    """Get Marp CSS for a theme."""
    theme = THEMES.get(name)
    return theme.get("marp_css") if theme else None


def get_theme_colors(name: str) -> dict | None:
    """Get color palette for a theme."""
    theme = THEMES.get(name)
    return theme.get("colors") if theme else None


def list_themes() -> dict[str, dict]:
    """List all available themes with metadata."""
    return {
        name: {
            "name": data["name"],
            "description": data["description"],
            "aesthetic": data["aesthetic"],
        }
        for name, data in THEMES.items()
    }


def list_palettes() -> dict[str, dict]:
    """List all available color palettes."""
    return PALETTES


def get_palette(name: str) -> dict | None:
    """Get a color palette by name."""
    return PALETTES.get(name)
