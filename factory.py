from PIL import Image, ImageDraw
import numpy as np
import random

# --- WEAPON PRIMITIVES v2.9 ---

def apply_geometric_mask(draw, bounds, num_shapes, transparency):
    """Draws random, semi-transparent shapes within the given bounds."""
    for _ in range(num_shapes):
        x0 = random.randint(bounds[0], max(bounds[0], bounds[2] - 10))
        y0 = random.randint(bounds[1], max(bounds[1], bounds[3] - 10))
        x1 = x0 + random.randint(10, 90)
        y1 = y0 + random.randint(10, 90)
        fill_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(transparency[0], transparency[1]))
        draw.rectangle([(x0, y0), (x1, y1)], fill=fill_color, outline=None)

def apply_line_mask(draw, bounds, num_lines, width_range):
    """Draws random lines within the given bounds."""
    if bounds[0] >= bounds[2] or bounds[1] >= bounds[3]: return # Skip if bounds are invalid
    for _ in range(num_lines):
        start_point = (random.randint(bounds[0], bounds[2]), random.randint(bounds[1], bounds[3]))
        end_point = (random.randint(bounds[0], bounds[2]), random.randint(bounds[1], bounds[3]))
        line_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        line_width = random.randint(width_range[0], width_range[1])
        draw.line([start_point, end_point], fill=line_color, width=line_width)

def apply_pixel_scatter(image, bounds, num_scatters):
    """Takes small patches from the heat zone and pastes them elsewhere in the zone."""
    img_width = bounds[2] - bounds[0]
    img_height = bounds[3] - bounds[1]
    if img_width < 30 or img_height < 30: return image # Skip if zone is too small
    for _ in range(num_scatters):
        src_w, src_h = random.randint(10, 30), random.randint(10, 30)
        src_x = bounds[0] + random.randint(0, img_width - src_w)
        src_y = bounds[1] + random.randint(0, img_height - src_h)
        patch = image.crop((src_x, src_y, src_x + src_w, src_y + src_h))
        dest_x = bounds[0] + random.randint(0, img_width - src_w)
        dest_y = bounds[1] + random.randint(0, img_height - src_h)
        image.paste(patch, (dest_x, dest_y))
    return image

def apply_glass_storm(draw, bounds, num_shards):
    """Scatters thousands of tiny, semi-transparent shards of color in the heat zone."""
    if bounds[0] >= bounds[2] or bounds[1] >= bounds[3]: return # Skip if bounds are invalid
    for _ in range(num_shards):
        x = random.randint(bounds[0], bounds[2])
        y = random.randint(bounds[1], bounds[3])
        shard_size = random.randint(1, 3)
        shard_color = (random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(80, 150))
        draw.rectangle([(x,y), (x+shard_size, y+shard_size)], fill=shard_color)

def apply_t_junction_attack(draw, heat_zone_bounds, num_junctions=50):
    """Draws lines that terminate on the edge of the heat zone to confuse CNNs."""
    hz_x_min, hz_y_min, hz_x_max, hz_y_max = heat_zone_bounds
    if hz_x_min >= hz_x_max or hz_y_min >= hz_y_max: return
    
    for _ in range(num_junctions):
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        start_x = random.randint(hz_x_min, hz_x_max)
        start_y = random.randint(hz_y_min, hz_y_max)
        
        if edge == 'top':
            end_point = (random.randint(start_x - 20, start_x + 20), hz_y_min)
        elif edge == 'bottom':
            end_point = (random.randint(start_x - 20, start_x + 20), hz_y_max)
        elif edge == 'left':
            end_point = (hz_x_min, random.randint(start_y - 20, start_y + 20))
        else:
            end_point = (hz_x_max, random.randint(start_y - 20, start_y + 20))
            
        line_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.line([(start_x, start_y), end_point], fill=line_color, width=random.randint(1, 3))
        
def apply_grid_pattern(draw, bounds, grid_size_base=15, pattern_intensity_scale=1.0):
    """Applies a repeating grid pattern."""
    x_min, y_min, x_max, y_max = bounds
    if x_min >= x_max or y_min >= y_max: return

    grid_size = max(2, int(grid_size_base * (1.0 - (pattern_intensity_scale * 0.75))))
    
    for x in range(x_min, x_max, grid_size):
        line_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), int(150 * pattern_intensity_scale))
        draw.line([(x, y_min), (x, y_max)], fill=line_color, width=1)
    for y in range(y_min, y_max, grid_size):
        line_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), int(150 * pattern_intensity_scale))
        draw.line([(x_min, y), (x_max, y)], fill=line_color, width=1)


# --- MASTER STRATEGY v2.9: PROJECT OVERLORD ---
def generate_overlord_mask(image_input, saliency_map, intensity=0.7):
    """Generates the final, most powerful adversarial mask."""
    if not (0.0 <= intensity <= 1.0):
        raise ValueError("Intensity must be between 0.0 and 1.0")

    image = image_input.copy()
    draw = ImageDraw.Draw(image, "RGBA")
    img_width, img_height = image.size
    saliency_height, saliency_width = saliency_map.shape

    threshold = np.percentile(saliency_map, 85)
    hot_pixels = np.argwhere(saliency_map >= threshold)
    
    if len(hot_pixels) == 0:
        min_saliency_y, min_saliency_x = saliency_height // 4, saliency_width // 4
        max_saliency_y, max_saliency_x = min_saliency_y * 3, min_saliency_x * 3
    else:
        min_saliency_y, min_saliency_x = hot_pixels.min(axis=0)
        max_saliency_y, max_saliency_x = hot_pixels.max(axis=0)

    x_scale = img_width / saliency_width
    y_scale = img_height / saliency_height
    heat_zone_bounds = [
        int(min_saliency_x * x_scale), int(min_saliency_y * y_scale),
        int(max_saliency_x * x_scale), int(max_saliency_y * y_scale)
    ]
    global_bounds = [0, 0, img_width, img_height]

    # STAGE 1: Global Suppression
    apply_geometric_mask(draw, global_bounds, num_shapes=int(40 * intensity), transparency=(40, 90))
    apply_line_mask(draw, global_bounds, num_lines=int(30 * intensity), width_range=(1, 2))

    # STAGE 2: Concentrated Multi-Vector Strike on Heat Zone
    apply_geometric_mask(draw, heat_zone_bounds, num_shapes=int(60 * intensity), transparency=(100, 200))
    apply_line_mask(draw, heat_zone_bounds, num_lines=int(50 * intensity), width_range=(2, 6))
    apply_t_junction_attack(draw, heat_zone_bounds, num_junctions=int(50 * intensity))
    apply_grid_pattern(draw, heat_zone_bounds, grid_size_base=20, pattern_intensity_scale=intensity)

    # STAGE 3: Final Data Corruption
    image = apply_pixel_scatter(image, heat_zone_bounds, num_scatters=int(60 * intensity))
    draw = ImageDraw.Draw(image, "RGBA")
    apply_glass_storm(draw, heat_zone_bounds, num_shards=int(1200 * intensity))

    return image