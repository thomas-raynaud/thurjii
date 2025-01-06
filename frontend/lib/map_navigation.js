const TILE_SIZE = 256
const EQUATOR = 40075016.68557849

const get_map_coords = (coords, e, element) => {
    let mouse_pos = get_mouse_pos(e, element)
    return {
        x: (Math.floor(mouse_pos.x / TILE_SIZE) + (coords.x + 1) + (((mouse_pos.x % TILE_SIZE) - (TILE_SIZE - element.scrollLeft)) / TILE_SIZE)) / Math.pow(2, coords.z),
        y: (Math.floor(mouse_pos.y / TILE_SIZE) + (coords.y + 1) + (((mouse_pos.y % TILE_SIZE) - (TILE_SIZE - element.scrollTop)) / TILE_SIZE)) / Math.pow(2, coords.z)
    }
}

const get_mouse_pos = (event, element) => {
    return {
        x: event.clientX + document.documentElement.scrollLeft - element.parentElement.offsetLeft,
        y: event.clientY + document.documentElement.scrollTop - element.parentElement.offsetTop
    }
}

const get_viewport_coords = (event, element, dims_vp) => {
    let mouse_pos = get_mouse_pos(event, element)
    return {
        x: mouse_pos.x / (dims_vp[0] * TILE_SIZE),
        y: mouse_pos.y / (dims_vp[1] * TILE_SIZE),
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