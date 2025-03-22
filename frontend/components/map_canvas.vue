<template>
    <canvas ref="canvas"></canvas>
</template>

<style scoped>
    canvas {
        position: absolute;
        z-index: 1;
    }
</style>

<script setup>
    import { useTemplateRef, onMounted } from 'vue'

    import {
        get_dims_map,
        get_mouse_pos,
        get_map_coords,
        from_mercator_to_rel_coords,
        get_tile_size_from_zoom,
    } from '../lib/map_navigation'
    import {
        get_distance,
        translate,
        rotate,
        get_lines_intersection_point
    } from '../lib/geometry'
    import { degrees_to_radians } from '../lib/math'
    import { map_store } from '../stores/map_store'
    import { STATE } from '../lib/enums'

    const props = defineProps([ 'nbTilesX', 'nbTilesY' ])
    const nb_tiles_x = parseInt(props.nbTilesX)
    const nb_tiles_y = parseInt(props.nbTilesY)

    const canvas = useTemplateRef("canvas")

    let ctx
    let line_cursor = {
        x: -1,
        y: -1
    }
    let line_theta
    let line_step

    onMounted(() => {
        let dims = get_dims_map(nb_tiles_x, nb_tiles_y)
        canvas.value.style["width"] = dims.width + "px"
        canvas.value.style["height"] = dims.height + "px"
        canvas.value.width = dims.width
        canvas.value.height = dims.height
        ctx = canvas.value.getContext("2d")
        map_store.state = STATE.SELECT_REGION
        line_theta = 0
        line_step = 10
        draw()
    })

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

    const draw = () => {
        ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)
        if (map_store.region.length == 0)
            return
        let region_on_canvas = []
        for (let i = 0; i < map_store.region.length; i++) {
            region_on_canvas[i] = from_mercator_to_canvas_pos(map_store.region[i])
        }
        
        ctx.strokeStyle = 'red'
        ctx.lineWidth = '1'
        ctx.beginPath()
        let poly = new Path2D()
        ctx.moveTo(region_on_canvas[0].x, region_on_canvas[0].y)
        poly.moveTo(region_on_canvas[0].x, region_on_canvas[0].y)
        for (let i = 1; i < map_store.region.length; i++) {
            ctx.lineTo(region_on_canvas[i].x, region_on_canvas[i].y)
            poly.lineTo(region_on_canvas[i].x, region_on_canvas[i].y)
        }
        poly.closePath()
        ctx.setLineDash([])
        ctx.stroke()
        let cursor_coords = from_rel_coords_to_canvas_pos(map_store.cursor_rel_coords)
        if (map_store.state == STATE.SELECT_REGION) {
            ctx.beginPath()
            ctx.setLineDash([1, 2])
            ctx.moveTo(region_on_canvas.at(-1).x, region_on_canvas.at(-1).y)
            ctx.lineTo(cursor_coords.x, cursor_coords.y)
            ctx.stroke()
        }
        ctx.fillStyle = "rgba(255, 0, 0, 0.25)"
        ctx.fill(poly, "evenodd")
        if (map_store.state == STATE.SELECT_REGION && map_store.region.length >= 2) {
            let triangle_cursor = new Path2D()
            triangle_cursor.moveTo(region_on_canvas.at(-1).x, region_on_canvas.at(-1).y)
            triangle_cursor.lineTo(cursor_coords.x, cursor_coords.y)
            triangle_cursor.lineTo(region_on_canvas[0].x, region_on_canvas[0].y)
            triangle_cursor.closePath()
            ctx.fill(triangle_cursor, "evenodd")
        }
        if (map_store.state == STATE.PLACE_LINES) {
            // Show line cursor
            let line_cursor_canvas = from_rel_coords_to_canvas_pos(line_cursor)
            ctx.beginPath()
            ctx.arc(line_cursor_canvas.x, line_cursor_canvas.y, 2, 0, 2 * Math.PI)
            ctx.fillStyle = "black"
            ctx.fill()
            ctx.beginPath()
            ctx.arc(line_cursor_canvas.x, line_cursor_canvas.y, 1, 0, 2 * Math.PI)
            ctx.fillStyle = "white"
            ctx.fill()
            // Draw lines
            for (let i = 0; i < map_store.lines.length; i++) {
                ctx.beginPath()
                ctx.strokeStyle = 'green'
                ctx.lineWidth = '1'
                ctx.moveTo(map_store.lines[i].start.x, map_store.lines[i].start.y)
                ctx.lineTo(map_store.lines[i].end.x, map_store.lines[i].end.y)
                ctx.stroke()
            }
        }
    }

    const get_lines_in_direction = (start_pos, dir_step) => {
        let line_cursor_canvas = from_rel_coords_to_canvas_pos(line_cursor)
        let theta_rad = degrees_to_radians(line_theta)
        let intersections
        let line_pos = start_pos
        // p1 space
        let p0 = { x: 20, y: 0 }
        let p2 = { x: -20, y: 0 }
        let p0t, p2t // p0 and p2 transformed in other spaces
        do {
            intersections = []
            // cursor space
            p0t = rotate(p0, Math.PI / 2)
            p2t = rotate(p2, Math.PI / 2)
            p0t = translate(p0t, { x: line_pos, y: 0 })
            p2t = translate(p2t, { x: line_pos, y: 0 })
            // world space
            p0t = rotate(p0t, theta_rad)
            p2t = rotate(p2t, theta_rad)
            p0t = translate(p0t, line_cursor_canvas)
            p2t = translate(p2t, line_cursor_canvas)
            for (let i = 0; i < map_store.region.length; i++) {
                let c = from_mercator_to_canvas_pos(map_store.region[i])
                let d = from_mercator_to_canvas_pos(map_store.region[(i + 1) % map_store.region.length])
                let intersection = get_lines_intersection_point(p0t, p2t, c, d)
                if (
                    intersection.x != Number.MAX_VALUE
                    && intersection.x >= Math.min(c.x, d.x)
                    && intersection.x <= Math.max(c.x, d.x)
                    && intersection.y >= Math.min(c.y, d.y)
                    && intersection.y <= Math.max(c.y, d.y)
                )
                    intersections.push(intersection)
            }
            if (intersections.length >= 2) {
                if (dir_step < 0)
                    map_store.lines.unshift({ start: intersections[0], end: intersections[1] })
                else
                    map_store.lines.push({ start: intersections[0], end: intersections[1] })
            }
            line_pos += dir_step
        } while (intersections.length > 0)
    }

    const compute_lines = () => {
        map_store.lines = []
        get_lines_in_direction(0, line_step)
        get_lines_in_direction(-line_step, -line_step)
    }

    const start_line_panning = () => { map_store.line_panning = true }
    const stop_line_panning = () => { map_store.line_panning = false }
    const start_line_rotating = () => { map_store.line_rotating = true }
    const stop_line_rotating = () => { map_store.line_rotating = false }
    const start_line_spreading = () => { map_store.line_spreading = true }
    const stop_line_spreading = () => { map_store.line_spreading = false }

    const pan_lines = (e) => {
        line_cursor = get_map_coords(map_store.coords, map_store.offset_display, [ e.clientX, e.clientY ], canvas.value)
        compute_lines()
    }

    const rotate_lines = (e) => {
        let pos = get_mouse_pos([ e.clientX, e.clientY ], canvas.value)
        let dims_map = get_dims_map(nb_tiles_x, nb_tiles_y)
        line_theta = ((pos.x / dims_map.width) - 0.5) * 360
        compute_lines()
    }

    const spread_lines = (e) => {
        let line_cursor_canvas = from_rel_coords_to_canvas_pos(line_cursor)
        let pos = get_mouse_pos([ e.clientX, e.clientY ], canvas.value)
        line_step = Math.max(get_distance(line_cursor_canvas, pos), 2)
        compute_lines()
    }

    const set_line_cursor = (pos) => {
        line_cursor = pos
    }

    defineExpose({
        draw,
        start_line_panning, stop_line_panning,
        start_line_rotating, stop_line_rotating,
        start_line_spreading, stop_line_spreading,
        pan_lines, rotate_lines, spread_lines,
        compute_lines,
        set_line_cursor
    })
</script>