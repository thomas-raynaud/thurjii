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
        get_map_coords
    } from '../lib/map_navigation'
    import {
        get_distance,
        translate,
        rotate,
        get_lines_intersection_point
    } from '../lib/geometry'
    import {
        from_rel_coords_to_canvas_pos,
        from_mercator_to_canvas_pos,
        get_regions_canvas_coordinates,
        from_rgb_hex_color_to_rgba,
        draw_cursor_point,
        draw_lines
    } from '../lib/map_canvas_utils'
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
        map_store.current_region_ind = 0
        line_theta = 0
        line_step = 10
        draw()
    })

    const draw = () => {
        ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)
       
        let nb_regions = map_store.regions.length
        if (nb_regions == 0 || (nb_regions == 1 && map_store.regions[0].length == 0))
            return

        let canvas_regions = get_regions_canvas_coordinates()

        // Draw the regions
        ctx.lineWidth = '1'
        for (let i = 0; i < nb_regions; i++) {
            ctx.beginPath()
            let hex_color = "#" + map_store.regions_color[i]
            ctx.strokeStyle = hex_color
            ctx.fillStyle = from_rgb_hex_color_to_rgba(hex_color, 0.5)
            let poly = new Path2D()
            ctx.moveTo(canvas_regions[i][0].x, canvas_regions[i][0].y)
            poly.moveTo(canvas_regions[i][0].x, canvas_regions[i][0].y)
            for (let j = 1; j < canvas_regions[i].length; j++) {
                ctx.lineTo(canvas_regions[i][j].x, canvas_regions[i][j].y)
                poly.lineTo(canvas_regions[i][j].x, canvas_regions[i][j].y)
            }
            poly.closePath()
            ctx.setLineDash([])
            ctx.stroke()
            ctx.fill(poly, "evenodd")
        }
        if (map_store.state == STATE.ADD_PLOT_SECTION && canvas_regions[current_region_ind].length > 0) {
            // Draw a dash line from the last region point to the mouse cursor
            let current_canvas_region = canvas_regions[current_region_ind]
            let first_point = current_canvas_region[0]
            let last_point = current_canvas_region.at(-1)
            let cursor_coords = from_rel_coords_to_canvas_pos(map_store.cursor_rel_coords)
            ctx.beginPath()
            ctx.setLineDash([1, 2])
            ctx.moveTo(last_point.x, last_point.y)
            ctx.lineTo(cursor_coords.x, cursor_coords.y)
            ctx.stroke()
            if (current_canvas_region.length >= 2) {
                // Display the filled triangle with points : [ last region point, mouse cursor, first region point ]
                let triangle_cursor = new Path2D()
                triangle_cursor.moveTo(last_point.x, last_point.y)
                triangle_cursor.lineTo(cursor_coords.x, cursor_coords.y)
                triangle_cursor.lineTo(first_point.x, first_point.y)
                triangle_cursor.closePath()
                ctx.fill(triangle_cursor, "evenodd")
            }
        }
        if (map_store.state == STATE.EDIT_PLOT_SECTION) {
            let current_canvas_region = canvas_regions[current_region_ind]
            for (let point of current_canvas_region) {
                draw_cursor_point(ctx, point)
            }
        }

        // Draw the lines
        if (map_store.state == STATE.DISPLAY_PLOT ||
            map_store.state == STATE.EDIT_LINES_GLOBAL_PLACEMENT ||
            map_store.state == STATE.EDIT_LINES ||
            map_store.state == STATE.ADD_LINE ||
            map_store.state == STATE.REMOVE_LINE ||
            map_store.state == STATE.SELECT_LINES
        ) {
            draw_lines(ctx, map_store.lines, 'green', '2')
        }
        if (map_store.state == STATE.DISPLAY_PLOT || map_store.state == STATE.SELECT_LINES) {
            draw_lines(ctx, map_store.lines_highlighted, 'white', '2')
            draw_lines(ctx, map_store.lines_done, 'blue', '2')
        }
        if (map_store.state == STATE.EDIT_LINES) {
            draw_lines(ctx, [ map_store.lines[map_store.current_line_ind] ], 'white', '2')
        }
        if (map_store.state == STATE.EDIT_LINES_GLOBAL_PLACEMENT) {
            // Show global line cursor
            draw_cursor_point(ctx, line_cursor)
        }
        if (map_store.state == STATE.EDIT_LINES || map_store.state == STATE.REMOVE_LINE) {
            for (let line of map_store.lines) {
                for (let point of line) {
                    draw_cursor_point(ctx, point)
                }
            }
        }
        if (map_store.state == STATE.DISPLAY_VINEYARD && map_store.show_plot_names == true) {
            // Display the plot names
            ctx.fillStyle = "white"
            ctx.font = "12px"
            ctx.textBaseline = "middle"
            for (let i = 0; i < map_store.plot_centers.length; i++) {
                let text_pos = from_mercator_to_canvas_pos(map_store.plot_centers[i])
                let plot_name = map_store.plot_names[i]
                ctx.fillText(plot_name, (text_pos.x - ctx.measureText(plot_name).width / 2), text_pos.y)
            }
        }
        if (map_store.state == STATE.SELECT_LINES) {
            if (map_store.selecting_zone) {
                ctx.strokeStyle = "#0c07a3"
                ctx.fillStyle = "rgba(33, 96, 196, 0.25)"
                ctx.beginPath()
                let width = map_store.zone_selection.end.x - map_store.zone_selection.start.x
                let height = map_store.zone_selection.end.y - map_store.zone_selection.start.y
                ctx.rect(
                    map_store.zone_selection.start.x, map_store.zone_selection.start.y,
                    width, height
                )
                ctx.stroke()
                ctx.fill()
            }
        }
    }

    const compute_lines_in_direction = (start_pos, dir_step) => {
        // Fill map_store.lines with segments that intersect the plot's region
        // We start at position start_pos, get the 2 points that intersect the region from that point,
        // then we move in the line_theta direction by a dir_step step, compute the 2 intersecting points from there,
        // and so on until we do not longer intersect the region.
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
            let last_region = map_store.regions.at(-1)
            for (let i = 0; i < last_region.length; i++) {
                let c = from_mercator_to_canvas_pos(last_region[i])
                let d = from_mercator_to_canvas_pos(last_region[(i + 1) % last_region.length])
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
                    map_store.lines.unshift([ intersections[0], intersections[1] ])
                else
                    map_store.lines.push([ intersections[0], intersections[1] ])
            }
            line_pos += dir_step
        } while (intersections.length > 0)
    }

    const compute_lines = () => {
        map_store.lines = []
        compute_lines_in_direction(0, line_step)
        compute_lines_in_direction(-line_step, -line_step)
    }

    const pan_lines = (e) => {
        line_cursor = get_map_coords(map_store.coords, map_store.offset_display, [ e.clientX, e.clientY ], canvas.value.parentElement)
        compute_lines()
    }

    const rotate_lines = (e) => {
        let pos = get_mouse_pos([ e.clientX, e.clientY ], canvas.value.parentElement)
        let dims_map = get_dims_map(nb_tiles_x, nb_tiles_y)
        line_theta = ((pos.x / dims_map.width) - 0.5) * 360
        compute_lines()
    }

    const spread_lines = (e) => {
        let line_cursor_canvas = from_rel_coords_to_canvas_pos(line_cursor)
        let pos = get_mouse_pos([ e.clientX, e.clientY ], canvas.value.parentElement)
        line_step = Math.max(get_distance(line_cursor_canvas, pos), 2)
        compute_lines()
    }

    const set_line_cursor = (pos) => {
        line_cursor = pos
    }

    defineExpose({
        draw,
        pan_lines, rotate_lines, spread_lines,
        compute_lines,
        set_line_cursor,
        from_mercator_to_canvas_pos
    })
</script>