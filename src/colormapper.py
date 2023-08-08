import matplotlib.colors as mcolors


def create_custom_cmap(color_set):
    cmap = mcolors.LinearSegmentedColormap.from_list('custom_cmap', color_set)
    return cmap


def generate_colors(elemets_amount, color_map):
    cmap = color_map
    generated_colors = []

    for i in range(elemets_amount):
        color_index = (i + 1) / (elemets_amount + 1)
        color = cmap(color_index)
        hex_color = mcolors.rgb2hex(color)
        generated_colors.append(hex_color)

    return generated_colors
