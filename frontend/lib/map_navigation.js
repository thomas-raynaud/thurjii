const TILE_SIZE = 256
const EQUATOR = 40075016.68557849

const get_map_coords = (coords, pos, element) => {
    let mouse_pos = get_mouse_pos(pos, element)
    let tile_size = element.children[0].height
    let z = Math.ceil(coords.z)
    return {
        x: (Math.floor(mouse_pos.x / tile_size) + (coords.x + 1) + (((mouse_pos.x % tile_size) - (tile_size - element.scrollLeft)) / tile_size)) / Math.pow(2, z),
        y: (Math.floor(mouse_pos.y / tile_size) + (coords.y + 1) + (((mouse_pos.y % tile_size) - (tile_size - element.scrollTop)) / tile_size)) / Math.pow(2, z)
    }
}

const get_mouse_pos = (pos, element) => {
    return {
        x: pos[0] + document.documentElement.scrollLeft - element.parentElement.offsetLeft,
        y: pos[1] + document.documentElement.scrollTop - element.parentElement.offsetTop
    }
}

const get_viewport_coords = (pos, element, dims_vp) => {
    let mouse_pos = get_mouse_pos(pos, element)
    let tile_size = element.children[0].height
    return {
        x: mouse_pos.x / (dims_vp[0] * tile_size),
        y: mouse_pos.y / (dims_vp[1] * tile_size),
    }
}

const from_rel_coords_to_mercator = (x, y) => {
    return {
        x: EQUATOR * ((x) - 0.5),
        y: EQUATOR * ((1 - y) - 0.5)
    }
}

const from_mercator_to_rel_coords = (x, y) => {
    return {
        x: x / EQUATOR + 0.5,
        y: -(y / EQUATOR - 0.5)
    }
}

const get_dims_map = (nb_tiles_x, nb_tiles_y) => {
    return {
        width: nb_tiles_x * TILE_SIZE,
        height: nb_tiles_y * TILE_SIZE
    }
}

export {
    TILE_SIZE,
    get_map_coords,
    get_mouse_pos,
    get_viewport_coords,
    get_dims_map,
    from_rel_coords_to_mercator, from_mercator_to_rel_coords
}