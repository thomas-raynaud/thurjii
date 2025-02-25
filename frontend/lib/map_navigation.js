import { map_store } from "../stores/map_store"

const TILE_SIZE = 256
const EQUATOR = 40075016.68557849

const get_tile_size_from_dom = (map_element) => {
    return map_element.children[0].height
}

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

const get_map_coords = (coords, offset, pos, map_element) => {
    let mouse_pos = get_mouse_pos(pos, map_element)
    let tile_size = get_tile_size_from_zoom(map_store.coords.z)
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

const get_nb_tiles_displayed = (map_element, zoom) => {
    let tile_size = get_tile_size_from_zoom(zoom)
    return {
        x: get_map_width(map_element) / tile_size,
        y: get_map_height(map_element) / tile_size
    }
}

export {
    TILE_SIZE,
    get_tile_size_from_zoom,
    get_map_coords,
    get_mouse_pos,
    get_viewport_coords,
    get_dims_map,
    get_nb_tiles_displayed,
    from_rel_coords_to_mercator, from_mercator_to_rel_coords,
}