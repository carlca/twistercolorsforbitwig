from PIL import Image
import random
import os
import colorsys
from typing import List, Tuple, Optional, cast
import json

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

def get_color_bias_input() -> dict[str, float]:
    """Asks the user for numerical color bias amounts for R, G, B (default 1.0 for no bias)."""
    bias_amounts = {} # Use a dictionary to store bias amounts

    print("\nEnter numerical bias amounts for Red, Green, Blue (default 1.0 for no bias):")

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

    if bias_amounts.get('red') == 1.0 and bias_amounts.get('green') == 1.0 and bias_amounts.get('blue') == 1.0:
        return None
    else:
        return bias_amounts

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def preview_mf_twister_palette(hex_codes, strategy, grid_rows, grid_cols, color_bias) -> None:
    """Displays a preview of the generated MF Twister palette with bias."""
    strategy_out = prettify_name(strategy)
    if color_bias:
        bias_text = f" (Bias: {color_bias.title()})" # e.g., " (Bias: Red)"
    else:
        bias_text = " (No Bias)"

    print(f"\nPreview of MF Twister Palette: {strategy_out}{bias_text} - {grid_cols}x{grid_rows} grid:")
    # Print the palette for preview with color blocks (similar to create_palette_image's print)
    for row in hex_codes:
        for hex_code in row:
            r = int(hex_code[1:3], 16)
            g = int(hex_code[3:5], 16)
            b = int(hex_code[5:7], 16)
            color_preview = f"\033[48;2;{r};{g};{b}m  \033[0m" # ANSI color block
            print(f"{color_preview} {hex_code}", end=" ")
        print()
    print()

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

def get_save_location_choice() -> None:
    """Asks the user for the output folder choice."""
    while True:
        choice1 = input("Save to Bitwig Color Palettes folder? (y/n, default: y): ").lower()
        if choice1 in ['y', 'yes', 'n', 'no', '']:
            if choice1 in ['y', 'yes', '']:
                return "bitwig_palettes"
        print("Please enter 'y' or 'n'.")

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def display_strategy(grid_cols, grid_rows, palette) -> None:
    unique_hex_codes_1d = list(set([hex_code for row in palette for hex_code in row])) # Flatten, convert to set, back to list
    palette_rows = []
    color_index = 0
    for row_index in range(grid_rows): # Reconstruct 2D palette with unique colors
        row_colors = []
        for col_index in range(grid_cols):
            if color_index < len(unique_hex_codes_1d): # Ensure we don't go out of bounds
                row_colors.append(unique_hex_codes_1d[color_index])
                color_index += 1
            else:
                row_colors.append("#000000") # Or some default color if we run out of unique colors (unlikely but for safety)
        palette_rows.append(row_colors)
    palette = [sort_palette_by_hue_saturation(row) for row in palette_rows] # Sort palette rows in-place!

    grid_lines = []
    for row_index in range(grid_rows):
        grid_lines.append(get_grid_row(palette, grid_lines, row_index, grid_cols))

    print(f"{grid_lines[0]}")
    for i in range(1, grid_rows):
        make_indent = " " * 2
        print(make_indent + grid_lines[i])
        print("")

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def prettify_name(name) -> str:
    name = name.replace('_', ' ').title()
    name = name.replace("Mf ", "MF ")
    return name

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def get_max_name_length(strategies) -> int:
    max_name_length = 0
    for strategy_name in strategies.values():
        max_name_length = max(max_name_length, len(prettify_name(strategy_name)))
    return max_name_length

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def sort_palette_by_hue_saturation(palette_hex_codes) -> List[str]:
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

def get_grid_row(palette, grid_lines, row_index, grid_cols) -> str:
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
        grid_choice = input("Choose grid size: '1' for 16x4 or '2' for 9x3 (default: 1): ")
        if grid_choice in ['1', '']:
            return 16, 4
        elif grid_choice == '2':
            return 9, 3
        else:
            print("Invalid choice. Please enter '1' or '2'.")

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

def create_palette_image(hex_codes, strategy, grid_rows, grid_cols) -> str:
    """Create and save an image from the palette hex codes, with folder choice and strategy for filename."""
    # Image dimensions
    image_width = grid_cols
    image_height = grid_rows

    # Create the image
    image = Image.new("RGB", (image_width, image_height))
    pixels = image.load()

    # Set pixel colors
    for row_index, row_codes in enumerate(hex_codes):
        for col_index, hex_code in enumerate(row_codes):
            r = int(hex_code[1:3], 16)
            g = int(hex_code[3:5], 16)
            b = int(hex_code[5:7], 16)
            pixels[col_index, row_index] = (r, g, b) # type: ignore

    # Generate unique filename (now with strategy name)
    # filename = generate_unique_filename(strategy, grid_rows, grid_cols)
    filename = generate_unique_filename()

    # Get user's folder choice
    save_location = get_save_location_choice()

    # Determine output folder based on user choice
    base_folder = os.getcwd()
    if save_location == "bitwig_palettes":
        output_folder = BITWIG_PALETTE_DIR
    elif save_location == "generated_palettes_subfolder":
        output_folder = os.path.join(BITWIG_PALETTE_DIR, GENERATED_PALETTES_SUBFOLDER)
    else: # save_location == "script_folder"
        output_folder = base_folder

    os.makedirs(output_folder, exist_ok=True) # Ensure folder exists
    filepath = os.path.join(output_folder, filename)

    # Save the image
    image.save(filepath)

    if save_location == "bitwig_palettes":
        print(f"Pixel palette image saved to Bitwig Color Palettes folder as: {filepath}")
    elif save_location == "generated_palettes_subfolder":
        print(f"Pixel palette image saved to '{GENERATED_PALETTES_SUBFOLDER}' subfolder as: {filepath}")
    else:
        print(f"Pixel palette image saved to script's folder as: {filepath}")

    # Print the palette for reference with color preview
    flat_hex_codes = [hex_code for row in hex_codes for hex_code in row] # Flatten 2D to 1D list
    sorted_hex_codes = sorted(flat_hex_codes) # Sort the 1D list of hex codes

    print("\nHex color codes in this palette:")
    hex_code_counter = 0
    for hex_code in sorted_hex_codes:
        r = int(hex_code[1:3], 16)
        g = int(hex_code[3:5], 16)
        b = int(hex_code[5:7], 16)
        color_preview = f"\033[48;2;{r};{g};{b}m  \033[0m" # ANSI color block
        print(f"{color_preview} {hex_code}", end=" ") # Print preview and hex code
        hex_code_counter += 1 # <--- INCREMENT COUNTER
        if (hex_code_counter % grid_cols) == 0: # <--- CONDITIONAL LINE BREAK
            print() # New line after every grid_cols hex codes
    print() # New line afte all hex codes

    return filename

# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░

# Main program
def main():
    print("\nWelcome to the Color Palette Generator!")
    print("---------------------------------------")

    generate_another = True

    while generate_another:
        # Get grid size choice
        grid_cols, grid_rows = get_grid_size_choice()
        grid_size_text = f"{grid_cols}x{grid_rows}"
        print(f"Generating {grid_size_text} palette.")

        # Get strategy choice from menu
        hex_codes = []
        bias_amounts = None  # Initialize color_bias_choice

        bias_preview_loop = True
        while bias_preview_loop:
            bias_amounts = get_color_bias_input()

            palette = generate_palette(grid_cols, grid_rows, bias_amounts)
            display_strategy(grid_cols, grid_rows, palette)

            while True: # Bias preview menu loop
                preview_action = input("Choose option: 'a' - Accept Palette, 's' - See Another Preview, 'b' - Choose Different Bias: ").lower()
                if preview_action == 'a':
                    bias_preview_loop = False
                    break
                elif preview_action == 's':
                    break
                elif preview_action == 'b':
                    bias_preview_loop = True
                    break
                else:
                    print("Invalid choice. Please enter 'a', 's', or 'b'.")


        # Create and save the palette image
        create_palette_image(hex_codes, strategy, grid_rows, grid_cols)

        # Ask if user wants to generate another palette
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
