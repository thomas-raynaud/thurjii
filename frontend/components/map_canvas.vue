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
    import { useTemplateRef, onMounted, watch } from 'vue'

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

    onMounted(() => {
        let dims = get_dims_map(nb_tiles_x, nb_tiles_y)
        canvas.value.style["width"] = dims.width + "px"
        canvas.value.style["height"] = dims.height + "px"
        canvas.value.width = dims.width
        canvas.value.height = dims.height
        ctx = canvas.value.getContext("2d")
        map_store.line_theta = 0
        map_store.line_step = 10
        draw()
    })

    const draw = () => {
        ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)
       
        let nb_regions = map_store.regions.length
        if (nb_regions == 0 || (nb_regions == 1 && map_store.regions[0].length == 0))
            return

        let canvas_regions = get_regions_canvas_coordinates(map_store.regions)

        // Draw the regions
        ctx.lineWidth = '1'
        for (let i = 0; i < nb_regions; i++) {
            if (canvas_regions[i].length == 0)
                continue
            ctx.beginPath()
            let hex_color = "#" + map_store.regions_color[i]
            ctx.strokeStyle = hex_color
            let opacity = 0.5
            if (    map_store.state == STATE.ADD_PLOT_SECTION ||
                    map_store.state == STATE.EDIT_LINES ||
                    map_store.state == STATE.EDIT_LINES_GLOBAL_PLACEMENT ||
                    map_store.state == STATE.ADD_LINE ||
                    map_store.state == STATE.REMOVE_LINE
            ) {
                opacity = 0.25
            }
            ctx.fillStyle = from_rgb_hex_color_to_rgba(hex_color, opacity)
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
        if (map_store.state == STATE.ADD_PLOT_SECTION && canvas_regions[map_store.current_region_ind].length > 0) {
            // Draw a dash line from the last region point to the mouse cursor
            let current_canvas_region = canvas_regions[map_store.current_region_ind]
            let first_point = current_canvas_region[0]
            let last_point = current_canvas_region.at(-1)
            let cursor_coords = from_rel_coords_to_canvas_pos(map_store.cursor_rel_coords)
            ctx.beginPath()
            ctx.lineWidth = '3'
            ctx.setLineDash([2, 3])
            ctx.moveTo(last_point.x, last_point.y)
            ctx.lineTo(cursor_coords.x, cursor_coords.y)
            let color = map_store.regions_color[map_store.current_region_ind]
            ctx.strokeStyle = color
            ctx.stroke()
            map_store.regions_color[map_store.current_region_ind]
            ctx.fillStyle = from_rgb_hex_color_to_rgba(color, 0.5)
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
            let current_canvas_region = canvas_regions[map_store.current_region_ind]
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
            for (let region_ind = 0; region_ind < map_store.regions.length; region_ind++) {
                draw_lines(ctx, map_store.lines[region_ind], 'green', '2')
            }
        }
        if (
            map_store.state == STATE.ADD_LINE ||
            map_store.state == STATE.EDIT_LINES ||
            map_store.state == STATE.REMOVE_LINE
        ) {
            draw_lines(ctx, map_store.lines_highlighted[map_store.current_region_ind], 'white', '2')
            
        }
        if (map_store.state == STATE.DISPLAY_PLOT || map_store.state == STATE.SELECT_LINES) {
            for (let i = 0; i < map_store.regions.length; i++) {
                draw_lines(ctx, map_store.lines_done[i], 'blue', '2')
                draw_lines(ctx, map_store.lines_highlighted[i], 'white', '2')
            }
            
        }
        if (map_store.state == STATE.EDIT_LINES_GLOBAL_PLACEMENT) {
            // Show line cursor
            draw_cursor_point(ctx, line_cursor)
        }
        if (map_store.state == STATE.ADD_LINE || map_store.state == STATE.EDIT_LINES || map_store.state == STATE.REMOVE_LINE) {
            if (line_cursor != null)
                draw_cursor_point(ctx, line_cursor)
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
        if (map_store.state == STATE.ADD_LINE && map_store.line_point_placed) {
            // Draw a dash line from the last point in the line to the mouse cursor
            let last_point = map_store.lines[map_store.current_region_ind][map_store.current_line_ind].at(-1)
            let last_point_canvas_pos = from_rel_coords_to_canvas_pos(last_point)
            let cursor_coords = from_rel_coords_to_canvas_pos(map_store.cursor_rel_coords)
            ctx.beginPath()
            ctx.lineWidth = '3'
            ctx.strokeStyle = "white"
            ctx.setLineDash([2, 3])
            ctx.moveTo(last_point_canvas_pos.x, last_point_canvas_pos.y)
            ctx.lineTo(cursor_coords.x, cursor_coords.y)
            ctx.stroke()
            // Draw line
            draw_lines(ctx, map_store.lines_highlighted[map_store.current_region_ind], 'white', '2')
        }
    }

    const compute_lines_in_direction = (start_pos, dir_step) => {
        // Fill map_store.lines with segments that intersect the plot's region
        // We start at position start_pos, get the 2 points that intersect the region from that point,
        // then we move in the line_theta direction by a dir_step step, compute the 2 intersecting points from there,
        // and so on until we do not longer intersect the region.
        start_pos = Number(start_pos)
        dir_step = Number(dir_step)
        let theta_rad = degrees_to_radians(map_store.line_theta)
        let intersections
        let line_pos = start_pos
        // p1 space
        let p0 = { x: 20, y: 0 }
        let p2 = { x: -20, y: 0 }
        let p0t, p2t // p0 and p2 transformed in other spaces
        let line_cursor_canvas = from_rel_coords_to_canvas_pos(line_cursor)
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
            let current_region = map_store.regions[map_store.current_region_ind]
            for (let i = 0; i < current_region.length; i++) {
                let c = from_mercator_to_canvas_pos(current_region[i])
                let d = from_mercator_to_canvas_pos(current_region[(i + 1) % current_region.length])
                let intersection = get_lines_intersection_point(p0t, p2t, c, d)
                if (
                    intersection.x != Number.MAX_VALUE
                    && intersection.x >= Math.min(c.x, d.x)
                    && intersection.x <= Math.max(c.x, d.x)
                    && intersection.y >= Math.min(c.y, d.y)
                    && intersection.y <= Math.max(c.y, d.y)
                ) {
                    let intersection_rel_coords = get_map_coords(map_store.coords, map_store.offset_display, intersection)
                    intersections.push(intersection_rel_coords)
                }
            }
            if (intersections.length >= 2) {
                if (dir_step < 0)
                    map_store.lines[map_store.current_region_ind].unshift([ intersections[0], intersections[1] ])
                else
                    map_store.lines[map_store.current_region_ind].push([ intersections[0], intersections[1] ])
            }
            line_pos += dir_step
        } while (intersections.length > 0)
    }

    const compute_lines = () => {
        map_store.lines[map_store.current_region_ind] = []
        compute_lines_in_direction(0, map_store.line_step)
        compute_lines_in_direction(-map_store.line_step, -map_store.line_step)
        draw()
    }

    const pan_lines = (e) => {
        line_cursor = get_map_coords(map_store.coords, map_store.offset_display, { x: e.clientX, y: e.clientY }, canvas.value.parentElement)
        compute_lines()
    }

    const rotate_lines = (e) => {
        let pos = get_mouse_pos({ x: e.clientX, y: e.clientY }, canvas.value.parentElement)
        let dims_map = get_dims_map(nb_tiles_x, nb_tiles_y)
        map_store.line_theta = (((pos.x / dims_map.width) - 0.5) * 360) % 360
        if (map_store.line_theta < 0)
            map_store.line_theta = 360 + map_store.line_theta
        compute_lines()
    }

    const spread_lines = (e) => {
        let line_cursor_canvas = from_rel_coords_to_canvas_pos(line_cursor)
        let pos = get_mouse_pos({ x: e.clientX, y: e.clientY }, canvas.value.parentElement)
        map_store.line_step = Math.min(Math.max(get_distance(line_cursor_canvas, pos), map_store.line_spread_min), map_store.line_spread_max)
        compute_lines()
    }

    const set_line_cursor = (pos) => {
        line_cursor = pos
    }

    watch(() => map_store.line_theta, () => {
        if (map_store.state == STATE.EDIT_LINES_GLOBAL_PLACEMENT)
            compute_lines()
    })

    watch(() => map_store.line_step, () => {
        if (map_store.state == STATE.EDIT_LINES_GLOBAL_PLACEMENT)
            compute_lines()
    })

    defineExpose({
        draw,
        pan_lines, rotate_lines, spread_lines,
        compute_lines,
        set_line_cursor,
        from_rel_coords_to_canvas_pos,
        from_mercator_to_canvas_pos
    })
</script>