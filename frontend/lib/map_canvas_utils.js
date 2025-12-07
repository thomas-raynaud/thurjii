import { map_store } from '../stores/map_store'
import {
    get_tile_size_from_zoom
} from '../lib/map_navigation'
import {
    from_mercator_to_rel_coords
} from '../lib/map_navigation'

const from_rel_coords_to_canvas_pos = (rc) => {
    let tile_size = get_tile_size_from_zoom(map_store.coords.z)
    let tcx = rc.x * Math.pow(2, Math.ceil(map_store.coords.z))
    let tcy = rc.y * Math.pow(2, Math.ceil(map_store.coords.z))
    let pos_left = map_store.coords.x + (map_store.offset_display.x / tile_size)
    let pos_top = map_store.coords.y + (map_store.offset_display.y / tile_size)
    return {
        x: (tcx - pos_left) * tile_size,
        y: (tcy - pos_top) * tile_size
    }
}

const from_mercator_to_canvas_pos = (mc) => {
    let rc = from_mercator_to_rel_coords(mc)
    return from_rel_coords_to_canvas_pos(rc)
}

// Convert region's points from mercator coordinates to canvas coordinates
const get_region_canvas_coordinates = (region) => {
    let canvas_region = []
    for (let i = 0; i < region.length; i++) {
        canvas_region.push(from_mercator_to_canvas_pos(region[i]))
    }
    return canvas_region
}

const get_regions_canvas_coordinates = (regions) => {
    let canvas_regions = []
    for (let i = 0; i < regions.length; i++) {
        canvas_regions.push(get_region_canvas_coordinates(regions[i]))
    }
    return canvas_regions
}

const from_rgb_hex_color_to_rgba = (hex, opacity) => {
    let rgb = hex.replace(
        /^#?([a-f\d])([a-f\d])([a-f\d])$/i,
        (_m, r, g, b) => '#' + r + r + g + g + b + b
    ).substring(1).match(/.{2}/g).map(x => parseInt(x, 16))
    return "rgba(" + rgb[0] + ", " + rgb[1] + ", " + rgb[2] + ", " + opacity + ")"
}

const draw_cursor_point = (ctx, cursor_pos) => {
    let cursor_pos_canvas = from_rel_coords_to_canvas_pos(cursor_pos)
    ctx.beginPath()
    ctx.arc(cursor_pos_canvas.x, cursor_pos_canvas.y, 3, 0, 2 * Math.PI)
    ctx.fillStyle = "black"
    ctx.fill()
    ctx.beginPath()
    ctx.arc(cursor_pos_canvas.x, cursor_pos_canvas.y, 2, 0, 2 * Math.PI)
    ctx.fillStyle = "white"
    ctx.fill()
}

const draw_lines = (ctx, line_array, color, line_width) => {
    ctx.setLineDash([])
    for (let i = 0; i < line_array.length; i++) {
        let line = line_array[i].slice()
        ctx.beginPath()
        ctx.strokeStyle = color
        ctx.lineWidth = line_width
        let p = from_rel_coords_to_canvas_pos(line[0])
        ctx.moveTo(p.x, p.y)
        for (let point of line.slice(1)) {
            point = from_rel_coords_to_canvas_pos(point)
            ctx.lineTo(point.x, point.y)
        }
        ctx.stroke()
    }
}

export {
    from_rel_coords_to_canvas_pos,
    from_mercator_to_canvas_pos,
    get_region_canvas_coordinates,
    get_regions_canvas_coordinates,
    from_rgb_hex_color_to_rgba,
    draw_cursor_point,
    draw_lines
}