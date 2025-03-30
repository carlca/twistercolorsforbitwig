# Need new sort algorithm which splits the colors into
# red dominant, green dominant and blue dominant and sort within those

from PIL import Image
import random
import os
import colorsys
from typing import List, Tuple, Optional
import json
import colour
# from colour.models.rgb import RGB_Colourspace
from hilbertcurve.hilbertcurve import HilbertCurve
from colour.models.cie_luv import xy_to_Luv_uv
import numpy as np

# Dynamically determine the user's Documents directory and Bitwig path
USER_DOCUMENTS: str = os.path.expanduser("~/Documents")
BITWIG_PALETTE_DIR: str = os.path.join(USER_DOCUMENTS, "Bitwig Studio", "Color Palettes")
GENERATED_PALETTES_SUBFOLDER: str = "generated_palettes" # Define subfolder name
MF_TWISTER_ALL_COLORS: str = "mf_twister_all_colors.json" # Filename of JSON file
distinct_all_colors: List[List[int]]

try:
    with open(MF_TWISTER_ALL_COLORS, 'r') as f:
        distinct_all_colors = json.load(f)
except FileNotFoundError:
    print(f"Warning: {MF_TWISTER_ALL_COLORS} not found. 'mf_twister' strategy will use default colors or might not work.")
except json.JSONDecodeError:
    print(f"Error decoding JSON from {MF_TWISTER_ALL_COLORS}. File might be corrupted.")
except Exception as e:
    print(f"Error loading colors from {MF_TWISTER_ALL_COLORS}: {e}")

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def validate_hex_color(color: str) -> bool:
    """Validate if the input is a proper hex color code."""
    if not color.startswith('#') or len(color) != 7:
        return False
    try:
        # Check if the hex part can be converted to an integer
        int(color[1:], 16)
        return True
    except ValueError:
        return False

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def hsv_to_hex(h: float, s: float, v: float) -> str:
    """Convert HSV color to hex color code."""
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)
    return f"#{r:02X}{g:02X}{b:02X}"

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def rgb_to_hls(rgb_color: Tuple[int, int, int]) -> tuple[float, float, float]:
    r, g, b = [x / 255.0 for x in rgb_color]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h, l, s)

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def create_empty_palette(grid_rows: int, grid_cols: int) -> List[List[str]]:
    """Creates and returns an empty 3x9 or 4x16 palette (list of lists)."""
    return [
        ["" for _ in range(grid_cols)] for _ in range(grid_rows)
    ]

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def generate_palette(grid_rows: int, grid_cols: int, bias_amounts: Optional[dict[str, float]] = None) -> List[List[str]]:
    """Generate palette using pre-selected ALL maximally distinct colors from JSON file, ensuring unique colors,
        with optional numerical color bias amounts for R, G, B."""
    palette = create_empty_palette(grid_rows, grid_cols)
    global distinct_all_colors

    source_colors_rgb = distinct_all_colors
    json_file_label = "all"
    num_colors_needed = grid_rows * grid_cols
    unique_palette_hex_codes = set() # Use a set to track unique hex codes

    if not source_colors_rgb:
        print(f"Error: distinct RGB colors not loaded correctly for 'mf_twister' strategy ({json_file_label} colors). Check '{MF_TWISTER_ALL_COLORS}'.")
        return palette

    generated_colors_rgb = [] # To store generated RGB colors before hex conversion

    while len(unique_palette_hex_codes) < num_colors_needed: # Iterate until we have enough unique colors
        if bias_amounts: # Biased color selection
            biased_color_rgb_choices = get_biased_color_selection(source_colors_rgb, 1, bias_amounts) # Generate ONE biased color at a time
            candidate_color_rgb = biased_color_rgb_choices[0]
        else:
            candidate_color_rgb_list = random.sample(source_colors_rgb, 1)
            candidate_color_rgb = candidate_color_rgb_list[0]

        candidate_hex_code = hsv_to_hex(*colorsys.rgb_to_hsv(candidate_color_rgb[0]/255.0, candidate_color_rgb[1]/255.0, candidate_color_rgb[2]/255.0)) # Convert to hex

        if candidate_hex_code not in unique_palette_hex_codes:
            unique_palette_hex_codes.add(candidate_hex_code)
            generated_colors_rgb.append(candidate_color_rgb)

    # Now we have a set of unique hex codes, convert set back to list and then to 2D palette
    unique_palette_hex_list = list(unique_palette_hex_codes) # Convert set to list
    hex_colors = unique_palette_hex_list[:num_colors_needed] # Ensure palette size is not exceeded, trim if needed

    color_index = 0
    for col in range(grid_cols):
        for row in range(grid_rows):
            palette[row][col] = hex_colors[color_index]
            color_index += 1
    return palette

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def get_biased_color_selection(source_colors_rgb: List[List[int]], num_colors_needed: int, bias_amounts: dict[str, float]) -> List[Tuple[int, int, int]]:
     """Selects colors with numerical bias towards red, green, or blue using weighted random choice."""
     weights: List[float] = []
     biased_colors_rgb: List[Tuple[int, int, int]] = []

     bias_r = bias_amounts.get('red', 1.0)
     bias_g = bias_amounts.get('green', 1.0)
     bias_b = bias_amounts.get('blue', 1.0)

     for r, g, b in source_colors_rgb:
         weight = (r * bias_r) + (g * bias_g) + (b * bias_b)
         weights.append(weight)

     total_weight = sum(weights)
     if total_weight == 0:
         probabilities = [1.0 / len(weights)] * len(weights)
     else:
         probabilities = [w / total_weight for w in weights]

     choices = random.choices(source_colors_rgb, weights=probabilities, k=num_colors_needed)
     tuple_choices: List[Tuple[int, int, int]] = [(color[0], color[1], color[2]) for color in choices] # Explicit tuple construction
     biased_colors_rgb.extend(tuple_choices)
     return biased_colors_rgb

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def get_random_color_bias_input() -> Optional[dict[str, float]]:
    bias_amounts: Optional[dict[str, float]] = {}
    print("\nGenerating 3 sets of random bias amounts...")

    r = round(random.uniform(0.5, 2.0), 2)  # Example range, adjust as needed
    g = round(random.uniform(0.5, 2.0), 2)
    b = round(random.uniform(0.5, 2.0), 2)
    print(f"  Red={r}, Green={g}, Blue={b}")

    r = round(random.uniform(0.5, 2.0), 2)
    g = round(random.uniform(0.5, 2.0), 2)
    b = round(random.uniform(0.5, 2.0), 2)
    bias_amounts = {'red': r, 'green': g, 'blue': b}

    return bias_amounts

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def get_manual_color_bias_inputs() -> Optional[dict[str, float]]:
    bias_amounts: Optional[dict[str, float]] = {}
    print("\nEnter numerical bias amounts for Red, Green, Blue (default 1.0 for no bias):\n")

    while True: # Loop for Red bias input
        r_bias_input = input("  Red bias amount (default 1.0): ").strip() # Add .strip() to remove whitespace
        if r_bias_input == '':
            bias_amounts['red'] = 1.0 # Default for Red
            break
        try:
            bias_amounts['red'] = float(r_bias_input)
            break
        except ValueError:
            print("Invalid input. Please enter a valid number for Red bias (e.g., 1, 1.0, 1.5).") # More informative message

    while True: # Loop for Green bias input
        g_bias_input = input("  Green bias amount (default 1.0): ").strip() # Add .strip()
        if g_bias_input == '':
            bias_amounts['green'] = 1.0 # Default for Green
            break
        try:
            bias_amounts['green'] = float(g_bias_input)
            break
        except ValueError:
            print("Invalid input. Please enter a valid number for Green bias (e.g., 1, 1.0, 1.5).") # More informative message

    while True: # Loop for Blue bias input
        b_bias_input = input("  Blue bias amount (default 1.0): ").strip() # Add .strip()
        if b_bias_input == '':
            bias_amounts['blue'] = 1.0 # Default for Blue
            break
        try:
            bias_amounts['blue'] = float(b_bias_input)
            break
        except ValueError:
            print("Invalid input. Please enter a valid number for Blue bias (e.g., 1, 1.0, 1.5).") # More informative message

    return bias_amounts

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def get_color_bias_input(default_to_random: bool, default_to_manual: bool) -> Optional[dict[str, float]]:
    """Asks the user for numerical color bias amounts for R, G, B (default 1.0 for no bias)."""
    bias_amounts: Optional[dict[str, float]] = {}

    while True:
        if default_to_random:
            bias_amounts = get_random_color_bias_input()
            break
        if default_to_manual:
            bias_amounts = get_manual_color_bias_inputs()
            break
        else:
            print("\nChoose bias input method:\n")
            print("  1: Randomly Generated Bias Amounts (3 options)")
            print("  2: Manual Input (Enter numerical bias amounts for Red, Green, Blue)\n")

            while True:
                choice = input("Enter choice (1 or 2, default: 1): ").strip()
                if choice == '' or choice == '1':
                    bias_amounts = get_random_color_bias_input()
                    break
                if choice == '2':
                    bias_amounts = get_manual_color_bias_inputs()
                    break
            break

    if bias_amounts and bias_amounts.get('red') == 1.0 and bias_amounts.get('green') == 1.0 and bias_amounts.get('blue') == 1.0:
        return None
    else:
        return bias_amounts

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def generate_unique_filename() -> str:
    strategy ="mf_twister"
    counter_file = f"{strategy}_counter.txt"

    if os.path.exists(counter_file):
        with open(counter_file, "r") as f:
            try:
                counter = int(f.read())
            except ValueError:
                counter = 1
    else:
        counter = 1

    counter_str = str(counter).zfill(3)
    file_name = f"{strategy}_palette_{counter_str}"

    try:
        with open(counter_file, "w") as f:
            f.write(str(counter + 1))
    except Exception:
        print("Error writing to counter file.")

    return f"{file_name}.png"

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def get_save_location_choice() -> str:
    """Asks the user for the output folder choice."""
    while True:
        choice1 = input("\nSave to Bitwig Color Palettes folder? (y/n, default: y): ").lower()
        if choice1 in ['y', 'yes', 'n', 'no', '']:
            if choice1 in ['y', 'yes', '']:
                return "bitwig_palettes"
        print("Please enter 'y' or 'n'.")

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def display_strategy_original(grid_cols: int, grid_rows: int, palette: List[List[str]]) -> None:
    # print(f"\nDEBUG - display_strategy_original: palette; {palette}\n")
    palette_1d = list(set([hex_code for row in palette for hex_code in row])) # Flatten, convert to set, back to list
    # print(f"\nDEBUG - display_strategy_original: palette_1d; {palette_1d}\n")
    palette_rows = []
    color_index = 0
    for row_index in range(grid_rows): # Reconstruct 2D palette with unique colors
        row_colors = []
        for col_index in range(grid_cols):
            if color_index < len(palette_1d): # Ensure we don't go out of bounds
                row_colors.append(palette_1d[color_index])
                color_index += 1
            else:
                row_colors.append("#000000") # Or some default 11color if we run out of unique colors (unlikely but for safety)
        palette_rows.append(row_colors)
    palette = [sort_palette_by_hue_saturation(row) for row in palette_rows] # Sort palette rows in-place!

    # print(f"\nDEBUG - display_strategy_original: palette_rows; {palette_rows}\n")
    # print(f"\nDEBUG - display_strategy_original: palette; {palette}\n")

    grid_lines = []
    for row_index in range(grid_rows):
        grid_lines.append(get_grid_row(palette, row_index, grid_cols))

    make_indent = " " * 4
    print(f"{make_indent + grid_lines[0]}")
    for i in range(1, grid_rows):
        print(make_indent + grid_lines[i])
    print("")

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def display_strategy_hls(grid_cols: int, grid_rows: int, palette: List[List[str]]) -> None:
    print("")
    palette_1d = [hex_code for row in palette for hex_code in row] # Flatten to 1D list
    unique_palette_hex_codes = sorted(list(set(palette_1d)), key=lambda hex_code: rgb_to_hls((int(hex_code[1:3], 16), int(hex_code[3:5], 16), int(hex_code[5:7], 16)))) # Flatten, convert to set, back to list and sort all colors

    palette_rows = []
    color_index = 0
    for row_index in range(grid_rows): # Reconstruct 2D palette with unique colors
        row_colors = []
        for col_index in range(grid_cols):
            if color_index < len(unique_palette_hex_codes): # Ensure we don't go out of bounds
                row_colors.append(unique_palette_hex_codes[color_index])
                color_index += 1
            else:
                row_colors.append("#000000") # Or some default color if we run out of unique colors (unlikely but for safety)
        palette_rows.append(row_colors)

    grid_lines = []
    for row_index in range(grid_rows):
        grid_lines.append(get_grid_row(palette_rows, row_index, grid_cols)) # Use the new palette_rows for display

    make_indent = " " * 4
    print(f"{make_indent + grid_lines[0]}")
    for i in range(1, grid_rows):
        print(make_indent + grid_lines[i])
    print("")

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def hex_to_rgb_normalised(hex_color: str) -> List[float]:
    """Convert hex color code to normalised RGB values (0.0-1.0)."""
    hex_color = hex_color.lstrip('#')
    return [int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4)]

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def get_hilbert_curve_index(hex_color: str, p: int = 10, n: int = 2) -> int:
    """
    Calculate the Hilbert curve index for a hex color using xy_to_Luv_uv.

    Args:
        hex_color: The hex color code (e.g., "#RRGGBB").
        p: Bits per dimension for Hilbert curve (grid size will be 2^p x 2^p).
        n: Number of dimensions (always 2 for u'v' chromaticity).

    Returns:
        The Hilbert curve index (integer).
    """
    rgb_normalised = hex_to_rgb_normalised(hex_color)

    # Access sRGB color space from the RGB_COLOURSPACES dictionary:
    try:
        srgb_colourspace = colour.RGB_COLOURSPACES["sRGB"] # <--- Try accessing sRGB from the dictionary
    except KeyError:
        print("Error: 'sRGB' not found in colour.RGB_COLOURSPACES. Check your colour-science installation.")
        return 0  # Or some other default value to prevent errors
    rgb_colour_science = np.array(rgb_normalised)

    # Convert sRGB to CIE XYZ
    xyz = colour.convert(rgb_colour_science, srgb_colourspace.name, 'CIE XYZ')

    # Convert CIE XYZ to CIE xy chromaticity coordinates
    xy = colour.XYZ_to_xy(xyz)

    # Get CIE Luv u'v' chromaticity coordinates from CIE xy
    luv_uv = xy_to_Luv_uv(xy)
    u_prime, v_prime = luv_uv  # xy_to_Luv_uv returns a tuple (u', v')

    # Scale and translate u' and v' to be in the range [0, 1] approximately, then to integers [0, 2^p - 1]
    u_prime_scaled = int((u_prime * 0.5 + 0.5) * ((2**p) - 1)) # Roughly from -1 to 1, scale to 0-1 and then to 0-1023 (for p=10)
    v_prime_scaled = int((v_prime * 0.5 + 0.5) * ((2**p) - 1)) # Same for v'

    # Ensure coordinates are within valid range [0, 2^p - 1]
    u_prime_scaled = max(0, min(2**p - 1, u_prime_scaled))
    v_prime_scaled = max(0, min(2**p - 1, v_prime_scaled))

    hc = HilbertCurve(p, n)
    hilbert_index = hc.distance_from_point([u_prime_scaled, v_prime_scaled])
    return hilbert_index

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def display_strategy_hilbert(grid_cols: int, grid_rows: int, palette: List[List[str]]) -> None:
    print("")
    palette_1d = [hex_code for row in palette for hex_code in row] # Flatten to 1D list
    unique_palette_hex_codes = list(set(palette_1d)) # Get unique colors

    # Sort by Hilbert curve index
    sorted_palette_hex_codes = sorted(unique_palette_hex_codes, key=get_hilbert_curve_index)

    palette_rows = []
    color_index = 0
    for row_index in range(grid_rows): # Reconstruct 2D palette with unique colors
        row_colors = []
        for col_index in range(grid_cols):
            if color_index < len(sorted_palette_hex_codes): # Ensure we don't go out of bounds
                row_colors.append(sorted_palette_hex_codes[color_index])
                color_index += 1
            else:
                row_colors.append("#000000") # Or some default color if we run out of unique colors (unlikely but for safety)
        palette_rows.append(row_colors)

    grid_lines = []
    for row_index in range(grid_rows):
        grid_lines.append(get_grid_row(palette_rows, row_index, grid_cols)) # Use the new palette_rows for display

    make_indent = " " * 4
    print(f"{make_indent + grid_lines[0]}")
    for i in range(1, grid_rows):
        print(make_indent + grid_lines[i])
    print("")

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def prettify_name(name: str) -> str:
    name = name.replace('_', ' ').title()
    name = name.replace("Mf ", "MF ")
    return name

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def sort_palette_by_hue_saturation(palette_hex_codes: List[str]) -> List[str]:
    palette_hsl_objects = []
    for hex_code in palette_hex_codes:
        r = int(hex_code[1:3], 16)
        g = int(hex_code[3:5], 16)
        b = int(hex_code[5:7], 16)
        rgb_color = (r, g, b)
        hsl = rgb_to_hls(rgb_color) # <--- Ensure it calls the RENAMED rgb_to_hls function
        palette_hsl_objects.append({'hex': hex_code, 'rgb': rgb_color, 'hsl': hsl})

    def sort_key(color_object): # Key function for sorting by Hue then Saturation
        h, s, l = color_object['hsl']
        return (h, s) # Sort primarily by Hue, then by Saturation

    sorted_palette_hsl_objects = sorted(palette_hsl_objects, key=sort_key)
    sorted_palette_hex_codes = [color['hex'] for color in sorted_palette_hsl_objects] # Extract hex codes back

    return sorted_palette_hex_codes

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def get_grid_row(palette: List[List[str]], row_index: int, grid_cols: int) -> str:
    grid_row_line = ""
    for col_index in range(grid_cols):
        hex_color = palette[row_index][col_index]
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        preview_block_ansi = f"\033[48;2;{r};{g};{b}m  \033[0m"  # 2-char block
        grid_row_line += preview_block_ansi
    return grid_row_line

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def get_grid_size_choice() -> Tuple[int, int]:
    """Asks the user to choose the grid size."""
    while True:
        grid_choice = input("\nChoose grid size: '1' for 16x4 or '2' for 9x3 (default: 1): ")
        if grid_choice in ['1', '']:
            return 16, 4
        elif grid_choice == '2':
            return 9, 3
        else:
            print("Invalid choice. Please enter '1' or '2'.")

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def create_palette_image(palette: List[List[str]], grid_rows: int, grid_cols: int) -> str:
    """Create and save an image from the palette hex codes, with folder choice and strategy for filename."""

    image_width = grid_cols
    image_height = grid_rows

    image = Image.new("RGB", (image_width, image_height))
    pixels = image.load()

    for col_index, col_codes in enumerate(palette):
        for row_index, color_code in enumerate(col_codes):
            r = int(color_code[1:3], 16)
            g = int(color_code[3:5], 16)
            b = int(color_code[5:7], 16)
            pixels[col_index, row_index] = (r, g, b) # type: ignore

    filename = generate_unique_filename()

    save_location = get_save_location_choice()

    base_folder = os.getcwd()
    if save_location == "bitwig_palettes":
        output_folder = BITWIG_PALETTE_DIR
    elif save_location == "generated_palettes_subfolder":
        output_folder = os.path.join(BITWIG_PALETTE_DIR, GENERATED_PALETTES_SUBFOLDER)
    else:
        output_folder = base_folder

    os.makedirs(output_folder, exist_ok=True)
    filepath = os.path.join(output_folder, filename)

    image.save(filepath)

    if save_location == "bitwig_palettes":
        print(f"Pixel palette image saved to Bitwig Color Palettes folder as: {filepath}")
    elif save_location == "generated_palettes_subfolder":
        print(f"Pixel palette image saved to '{GENERATED_PALETTES_SUBFOLDER}' subfolder as: {filepath}")
    else:
        print(f"Pixel palette image saved to script's folder as: {filepath}")

    flat_color_codes = [color_code for row in palette for color_code in row] # Flatten 2D to 1D list
    sorted_color_codes = sorted(flat_color_codes) # Sort the 1D list of hex codes

    print("\nHex color codes in this palette:\n")
    counter = 0

    for color_code in sorted_color_codes:
        r = int(color_code[1:3], 16)
        g = int(color_code[3:5], 16)
        b = int(color_code[5:7], 16)
        color_preview = f"\033[48;2;{r};{g};{b}m  \033[0m" # ANSI color block
        print(f"{color_preview} {color_code}", end=" ") # Print preview and hex code
        counter += 1
        if (counter % grid_cols) == 0:
            print()

    return filename

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

# Main program
def main():
    print("\nWelcome to the Color Palette Generator!")
    print("---------------------------------------")

    generate_another = True

    while generate_another:
        grid_cols, grid_rows = get_grid_size_choice()
        grid_size_text = f"{grid_cols}x{grid_rows}"
        print(f"\nGenerating {grid_size_text} palette.")

        palette = []
        bias_amounts = None

        bias_preview_loop = True
        default_to_random = False
        default_to_manual = False
        while bias_preview_loop:
            bias_amounts = get_color_bias_input(default_to_random, default_to_manual)

            palette = generate_palette(grid_cols, grid_rows, bias_amounts)

            display_strategy_original(grid_cols, grid_rows, palette)
            # display_strategy_hls(grid_cols, grid_rows, palette)
            # display_strategy_hilbert(grid_cols, grid_rows, palette)

            while True: # Bias preview menu loop
                preview_action = input("Choose option: 'n' - New random bias amounts (default), 'm' - Enter manual bias amounts, 'a' - Accept palette: ").lower()
                if preview_action == '' or preview_action == 'n':
                    default_to_random = True
                    default_to_manual = False
                    break
                if preview_action == 'm':
                    default_to_random = False
                    default_to_manual = True
                    break
                if preview_action == 'a':
                    bias_preview_loop = False
                    break
                print("Invalid choice. Please enter 'a', 's', or 'b'.")

        if palette:
            # print(f"DEBUG - main(): palette: {palette}")
            # palette is 16 x 4
            create_palette_image(palette, grid_rows, grid_cols)

        while True:
            another_input = input("\nWould you like to generate another palette? (y/n, default: y): ").lower()  # Modified prompt to show default
            if another_input == '':  # Check for empty input
                another = 'y'
            elif another_input in ['y', 'yes', 'n', 'no']:
                another = another_input  # Use user's input
                break
            else:
                print("Please enter 'y' or 'n'.")

        generate_another = another in ['y', 'yes']

    print("Thank you for using the Color Palette Generator!")

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

if __name__ == "__main__":
    main()

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
