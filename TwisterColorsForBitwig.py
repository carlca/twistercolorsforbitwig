import random
from typing import List, Tuple, Optional
from enum import Enum

class DominantColor(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

all_colors: List[Tuple[int, int, int]] = [
    (0, 0, 255), # 1 - Blue
    (0, 21, 255), # 2 - Blue (Green Rising)
    (0, 34, 255), #
    (0, 46, 255), #
    (0, 59, 255), #
    (0, 68, 255), #
    (0, 80, 255), #
    (0, 93, 255), #
    (0, 106, 255), #
    (0, 119, 255), #
    (0, 127, 255), #
    (0, 140, 255), #
    (0, 153, 255), #
    (0, 165, 255), #
    (0, 178, 255), #
    (0, 191, 255), #
    (0, 199, 255), #
    (0, 212, 255), #
    (0, 225, 255), #
    (0, 238, 255), #
    (0, 250, 255), # 21 - End of Blue's Reign
    (0, 255, 250), # 22 - Green (Blue Fading)
    (0, 255, 237), #
    (0, 255, 225), #
    (0, 255, 212), #
    (0, 255, 199), #
    (0, 255, 191), #
    (0, 255, 178), #
    (0, 255, 165), #
    (0, 255, 153), #
    (0, 255, 140), #
    (0, 255, 127), #
    (0, 255, 119), #
    (0, 255, 106), #
    (0, 255, 93), #
    (0, 255, 80), #
    (0, 255, 67), #
    (0, 255, 59), #
    (0, 255, 46), #
    (0, 255, 33), #
    (0, 255, 21), #
    (0, 255, 8), #
    (0, 255, 0), # 43 - Green
    (12, 255, 0), # 44 - Green/Red Rising
    (25, 255, 0), #
    (38, 255, 0), #
    (51, 255, 0), #
    (63, 255, 0), #
    (72, 255, 0), #
    (84, 255, 0), #
    (97, 255, 0), #
    (110, 255, 0), #
    (123, 255, 0), #
    (131, 255, 0), #
    (144, 255, 0), #
    (157, 255, 0), #
    (170, 255, 0), #
    (182, 255, 0), #
    (191, 255, 0), #
    (203, 255, 0), #
    (216, 255, 0), #
    (229, 255, 0), #
    (242, 255, 0), #
    (255, 246, 0), # 65 - Red, Green Fading
    (255, 233, 0), #
    (255, 220, 0), #
    (255, 208, 0), #
    (255, 195, 0), #
    (255, 187, 0), #
    (255, 174, 0), #
    (255, 161, 0), #
    (255, 148, 0), #
    (255, 135, 0), #
    (255, 127, 0), #
    (255, 114, 0), #
    (255, 102, 0), #
    (255, 89, 0), #
    (255, 76, 0), #
    (255, 63, 0), #
    (255, 55, 0), #
    (255, 42, 0), #
    (255, 29, 0), #
    (255, 16, 0), #
    (255, 4, 0), # 85 - End Red/Green Fading
    (255, 0, 4), # 86 - Red/ Blue Rising
    (255, 0, 16), #
    (255, 0, 29), #
    (255, 0, 42), #
    (255, 0, 55), #
    (255, 0, 63), #
    (255, 0, 76), #
    (255, 0, 89), #
    (255, 0, 102), #
    (255, 0, 114), #
    (255, 0, 127), #
    (255, 0, 135), #
    (255, 0, 148), #
    (255, 0, 161), #
    (255, 0, 174), #
    (255, 0, 186), #
    (255, 0, 195), #
    (255, 0, 208), #
    (255, 0, 221), #
    (255, 0, 233), #
    (255, 0, 246), #
    (242, 0, 255), # 108 - Blue/ Red Fading
    (229, 0, 255), #
    (216, 0, 255), #
    (204, 0, 255), #
    (191, 0, 255), #
    (182, 0, 255), #
    (169, 0, 255), #
    (157, 0, 255), #
    (144, 0, 255), #
    (131, 0, 255), #
    (123, 0, 255), #
    (110, 0, 255), #
    (97, 0, 255), #
    (85, 0, 255), #
    (72, 0, 255), #
    (63, 0, 255), #
    (50, 0, 255), #
    (38, 0, 255), #
    (25, 0, 255)] # 126 - Blue-ish

def create_palette(size: int) -> List[Tuple[int, int, int]]:
    return random.sample(all_colors, size)

def get_dom_colors(colors: List[Tuple[int, int, int]], dom_color: DominantColor) -> List[Tuple[int, int, int]]:
    dom_colors: List[Tuple[int, int, int]] = []
    for color in colors:
        r, g, b = color
        maximum = max(r, g, b) # Calculate the max only once
        if dom_color == DominantColor.RED and r == maximum:
            dom_colors.append(color)
        elif dom_color == DominantColor.GREEN and g == maximum:
            dom_colors.append(color)
        elif dom_color == DominantColor.BLUE and b == maximum:
            dom_colors.append(color)
    return dom_colors

def color_block(r: int, g: int, b: int, chars: int = 1) -> str:
    block = ''.join([" "] * chars)
    return f"\033[48;2;{r};{g};{b}m{block}\033[0m"

def get_dimensions(palette: List[Tuple[int, int, int]]) -> Tuple[int, int]:
    if len(palette) == 27:
        return (9, 3)
    if len(palette) == 64:
        return (16, 4)
    return (0, 0)

def display_palette(palette: List[Tuple[int, int, int]]) -> None:
    (cols, rows) = get_dimensions(palette)
    index = 0
    for row in range(rows):
        row_s = ''
        for col in range(cols):
            if index >= cols * rows:
                print(f"{row_s}")
                return
            r, g, b = palette[index]
            block = color_block(r, g, b, 2)
            row_s += block
            index += 1
        print(f"{row_s}")

def get_palette_size() -> int:
    while True:
        choice = input("Selected palette dimensions - '1' (9 x 3) or '2' (16 x 4): ").strip()
        palette_size = 0
        if choice == "1":
            palette_size = 27
        if choice == "2":
            palette_size = 64
        if palette_size > 0:
            return palette_size

def main():
    palette = create_palette(get_palette_size())
    print("")
    display_palette(palette)
    print("")
    sorted_palette = []
    sorted_palette += sorted(get_dom_colors(palette, DominantColor.RED))
    sorted_palette += sorted(get_dom_colors(palette, DominantColor.GREEN))
    sorted_palette += sorted(get_dom_colors(palette, DominantColor.BLUE))
    display_palette(sorted_palette)

if __name__ == "__main__":
    main()
