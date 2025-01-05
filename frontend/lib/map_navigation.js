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

const from_tile_coord_to_mercator = (x, y, z) => {
    return {
        x: EQUATOR * ((x) - 0.5),
        y: EQUATOR * ((1 - y) - 0.5)
    }
}

const from_mercator_to_tile_coord = (x, y, z) => {
    return {
        x: ((x + (EQUATOR / 2)) / EQUATOR) * Math.pow(2, z),
        y: ((-y + (EQUATOR / 2)) / EQUATOR) * Math.pow(2, z)
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
    get_dims_map,
    from_tile_coord_to_mercator, from_mercator_to_tile_coord
}