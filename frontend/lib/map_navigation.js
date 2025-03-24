import { map_store } from "../stores/map_store"

const TILE_SIZE = 256
const EQUATOR = 40075016.68557849

const get_tile_size_from_zoom = (zoom) => {
    let zoom_dec = zoom % 1
    if (zoom_dec == 0.0) return TILE_SIZE
    return 128 + 128 * zoom_dec
}

const get_map_width = (map_element) => {
    return map_element.clientWidth
}

const get_map_height = (map_element) => {
    return map_element.clientHeight
}

const get_map_coords = (coords, offset, pos, map_element=null) => {
    let mouse_pos = { x: pos[0], y: pos[1] }
    if (map_element != null)
        mouse_pos = get_mouse_pos(pos, map_element)
    let tile_size = get_tile_size_from_zoom(coords.z)
    let z = Math.ceil(coords.z)
    return {
        x: (Math.floor(mouse_pos.x / tile_size) + (coords.x + 1) + (((mouse_pos.x % tile_size) - (tile_size - offset.x)) / tile_size)) / Math.pow(2, z),
        y: (Math.floor(mouse_pos.y / tile_size) + (coords.y + 1) + (((mouse_pos.y % tile_size) - (tile_size - offset.y)) / tile_size)) / Math.pow(2, z)
    }
}

const get_mouse_pos = (pos, element) => {
    return {
        x: pos[0] + document.documentElement.scrollLeft - element.parentElement.offsetLeft,
        y: pos[1] + document.documentElement.scrollTop - element.parentElement.offsetTop
    }
}

const get_viewport_coords = (pos, map_element) => {
    let mouse_pos = get_mouse_pos(pos, map_element)
    return {
        x: mouse_pos.x / get_map_width(map_element),
        y: mouse_pos.y / get_map_height(map_element),
    }
}

const from_rel_coords_to_mercator = (x, y) => {
    return {
        x: EQUATOR * ((x) - 0.5),
        y: EQUATOR * ((1 - y) - 0.5)
    }
}

const from_mercator_to_rel_coords = (mc) => {
    return {
        x: mc.x / EQUATOR + 0.5,
        y: -(mc.y / EQUATOR - 0.5)
    }
}

const get_dims_map = (nb_tiles_x, nb_tiles_y) => {
    return {
        width: nb_tiles_x * TILE_SIZE,
        height: nb_tiles_y * TILE_SIZE
    }
}

const get_region_center_params = (region, dims_map) => {
    /*
    Get parameters to center the map display on the boundary box of the region
    @params
    - region: polygon, list of points representing the area of the region
    - dims_map: nb tiles in X and Y axis
    @return
    - pos: output position of region center (rel coords)
    - zoom: zoom level to enclose the region area
    */
    // Compute bounding box
    let region_min = { x: region[0].x, y: region[0].y }
    let region_max = { x: region[0].x, y: region[0].y }
    for (let i = 1; i < region.length; i++) {
        region_min.x = Math.min(region_min.x, region[i].x)
        region_min.y = Math.max(region_min.y, region[i].y)
        region_max.x = Math.max(region_max.x, region[i].x)
        region_max.y = Math.min(region_max.y, region[i].y)
    }
    let bb_start = from_mercator_to_rel_coords(region_min)
    let bb_end = from_mercator_to_rel_coords(region_max)
    // Get center position of boundary box
    let width_bb = bb_end.x - bb_start.x
    let height_bb = bb_end.y - bb_start.y
    let pos = { x: bb_start.x + width_bb / 2, y: bb_start.y + height_bb / 2 }
    // Get zoom parameter to enclose the boundary box
    let zoom_x = -Math.log2((width_bb * 1.1) / dims_map[0])
    let zoom_y = -Math.log2((height_bb * 1.1) / dims_map[1])
    let zoom = Math.min(zoom_x, zoom_y)
    return {
        pos: pos,
        zoom: zoom
    }
}

export {
    TILE_SIZE,
    get_tile_size_from_zoom,
    get_map_coords,
    get_mouse_pos,
    get_viewport_coords,
    get_dims_map,
    get_region_center_params,
    from_rel_coords_to_mercator, from_mercator_to_rel_coords,
}