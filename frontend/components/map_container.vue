<template>
    <div ref="container" class="map-container"
            oncontextmenu="return false"
            @mousemove="mousemove"
            @mousedown="mousedown"
            @mouseup="mouseup"
            @mouseleave="mouseleave"
            @wheel="mousewheel">
        <map-display
            ref="display"
            :nb-tiles-x="nb_tiles_x" :nb-tiles-y="nb_tiles_y"
        />
        <map-canvas
            ref="canvas"
            :nb-tiles-x="nb_tiles_x" :nb-tiles-y="nb_tiles_y"
        />
    </div>
</template>

<style scoped>
    .map-container {
        position: relative;
        padding: 0;
    }
</style>

<script setup>
    import { useTemplateRef, ref, onMounted, watch } from 'vue'

    import MapDisplay from './map_display.vue'
    import MapCanvas from './map_canvas.vue'
    import {
        get_dims_map,
        get_region_center_params,
        get_map_coords,
        from_rel_coords_to_mercator,
        get_mouse_pos
    } from '../lib/map_navigation'
    import {
        check_intersection_polygon,
        does_segment_intersect_rectangle,
        get_distance,
        get_distance_from_point_to_segment,
        dot_product,
        is_point_in_polygon
    } from '../lib/geometry'
    import { map_store } from '../stores/map_store'
    import { STATE, MOUSE_BUTTONS } from '../lib/enums'
    import {
        get_region_canvas_coordinates,
    } from '../lib/map_canvas_utils'

    const props = defineProps([ 'nbTilesX', 'nbTilesY' ])
    const nb_tiles_x = ref(parseInt(props.nbTilesX))
    const nb_tiles_y = ref(parseInt(props.nbTilesY))

    const container = useTemplateRef("container")
    const display = useTemplateRef("display")
    const canvas = useTemplateRef("canvas")

    const map_panning = ref(false)
    const line_panning = ref(false)
    const line_spreading = ref(false)
    const line_rotating = ref(false)

    onMounted(() => {
        let dims = get_dims_map(nb_tiles_x.value, nb_tiles_y.value)
        container.value.style["width"] = dims.width + "px"
        container.value.style["height"] = dims.height + "px"
        map_store.selecting_zone = false
        canvas.value.draw()
    })

    const store_coords_cookie = () => {
        $cookies.set("coords_x", map_store.coords.x)
        $cookies.set("coords_y", map_store.coords.y)
        $cookies.set("coords_z", map_store.coords.z)
        $cookies.set("offset_display_x", map_store.offset_display.x)
        $cookies.set("offset_display_y", map_store.offset_display.y)
    }

    const mousemove = (e) => {
        e.preventDefault()
        map_store.cursor_rel_coords = get_map_coords(
            map_store.coords, map_store.offset_display,
            { x: e.clientX, y: e.clientY },
            container.value
        )
        if (map_panning.value) {
            let display_nav_coords = display.value.pan(e)
            map_store.coords = display_nav_coords.coords
            map_store.offset_display = display_nav_coords.offset_display
            store_coords_cookie()
            canvas.value.draw()
        }
        else if (line_panning.value)   { canvas.value.pan_lines(e);     canvas.value.draw() }
        else if (line_rotating.value)  { canvas.value.rotate_lines(e);  canvas.value.draw() }
        else if (line_spreading.value) { canvas.value.spread_lines(e);  canvas.value.draw() }
        if (map_store.selecting_zone) {
            update_line_selection(e)
            canvas.value.draw()
        }
        if (map_store.state == STATE.ADD_PLOT_SECTION) {
            if (map_store.current_region_ind != -1 && map_store.regions[map_store.current_region_ind].length > 0)
                canvas.value.draw()
        }
        if (map_store.state == STATE.EDIT_LINES) {
            let cursor_pos = get_mouse_pos({ x: e.clientX, y: e.clientY }, container.value)
            if (map_store.line_point_dragged) {
                // Move the point dragged, if cursor is IN the region
                let canvas_region = get_region_canvas_coordinates(map_store.regions[map_store.current_region_ind])
                if (is_point_in_polygon(cursor_pos, canvas_region)) {
                    let cursor_map_pos = get_map_coords(
                        map_store.coords, map_store.offset_display,
                        cursor_pos
                    )
                    map_store.lines
                        [map_store.current_region_ind]
                        [map_store.current_line_ind]
                        [map_store.current_line_point_ind]
                        = cursor_map_pos
                    map_store.lines_highlighted[map_store.current_region_ind] = [
                        map_store.lines[map_store.current_region_ind][map_store.current_line_ind]
                    ]
                    canvas.value.set_line_cursor(cursor_map_pos)
                }
            }
            else {
                // Check if cursor close to a line. If so, display cursor on the point.
                const MIN_DIST_POINT = 4
                map_store.line_point_placed = false
                for (let i = 0; i < map_store.lines[map_store.current_region_ind].length; i++) {
                    let line = map_store.lines[map_store.current_region_ind][i]
                    for (let j = 0; j < line.length - 1; j++) {
                        let a = canvas.value.from_rel_coords_to_canvas_pos(line[j])
                        let b = canvas.value.from_rel_coords_to_canvas_pos(line[j + 1])
                        let c = cursor_pos
                        let cursor_dist = get_distance_from_point_to_segment(c, a, b)
                        if (cursor_dist <= MIN_DIST_POINT) {
                            let ab = { x: b.x - a.x, y: b.y - a.y }
                            let ac = { x: c.x - a.x, y: c.y - a.y }
                            let ab_dist = get_distance(a, b)
                            let proj_rel = dot_product(ab, ac) / Math.pow(ab_dist, 2)
                            map_store.line_point_placed = true
                            let proj_p = {
                                x: a.x + ab.x * proj_rel,
                                y: a.y + ab.y * proj_rel
                            }
                            canvas.value.set_line_cursor(
                                get_map_coords(
                                    map_store.coords, map_store.offset_display,
                                    proj_p
                                )
                            )
                            map_store.current_line_ind = i
                            map_store.current_line_point_ind = j
                            // Change cursor img TODO
                            break
                        }       
                    }
                    if (map_store.line_point_placed) {
                        break
                    }
                }
                if (!map_store.line_point_placed) {
                    canvas.value.set_line_cursor(null)
                }
            }
            canvas.value.draw()
        }
        if (map_store.state == STATE.ADD_LINE) {
            // Check if cursor in region
            let in_region = false
            let cursor_pos = get_mouse_pos({ x: e.clientX, y: e.clientY }, container.value)
            let canvas_region = get_region_canvas_coordinates(map_store.regions[map_store.current_region_ind])
            if (is_point_in_polygon(cursor_pos, canvas_region)) {
                in_region = true
            }
            let cursor_map_pos = get_map_coords(
                map_store.coords, map_store.offset_display,
                cursor_pos
            )
            if (in_region) {
                canvas.value.set_line_cursor(cursor_map_pos)
                canvas.value.draw()
            }
        }
        if (map_store.state == STATE.REMOVE_LINE) {
            // Check if mouse close to a line.
            // If so, highlight the line.
            const MIN_DIST_POINT = 3
            let cursor_pos = get_mouse_pos({ x: e.clientX, y: e.clientY }, container.value)
            let line_found = false
            map_store.current_line_ind = -1
            map_store.lines_highlighted[map_store.current_region_ind] = []
            for (let i = 0; i < map_store.lines[map_store.current_region_ind].length; i++) {
                let line = map_store.lines[map_store.current_region_ind][i]
                for (let j = 0; j < line.length - 1; j++) {
                    let a = canvas.value.from_rel_coords_to_canvas_pos(line[j])
                    let b = canvas.value.from_rel_coords_to_canvas_pos(line[j + 1])
                    let c = cursor_pos
                    let cursor_dist = get_distance_from_point_to_segment(c, a, b)
                    if (cursor_dist <= MIN_DIST_POINT) {
                        map_store.lines_highlighted[map_store.current_region_ind] = [ line ]
                        line_found = true
                        map_store.current_line_ind = i
                        break
                    }
                }
                if (line_found)
                    break
            }
            canvas.value.draw()
        }
    }

    const mousedown = (e) => {
        e.preventDefault()

        // Map panning
        if (map_store.state == STATE.ADD_PLOT_SECTION
                || map_store.state == STATE.EDIT_LINES
                || map_store.state == STATE.ADD_LINE
                || map_store.state == STATE.REMOVE_LINE) {
            if (e.button == MOUSE_BUTTONS.MIDDLE_CLICK) {
                display.value.start_panning(e)
                map_panning.value = true
            }
            canvas.value.draw()
        }

        if (map_store.state == STATE.ADD_PLOT_SECTION) {
            if (e.button == MOUSE_BUTTONS.LEFT_CLICK)
                add_point_to_region()
            else if (e.button == MOUSE_BUTTONS.RIGHT_CLICK)
                finish_region()
            canvas.value.draw()
        }
        else if (map_store.state == STATE.EDIT_LINES_GLOBAL_PLACEMENT) {
            if (e.button == MOUSE_BUTTONS.LEFT_CLICK && (e.shiftKey || e.ctrlKey)) {
                line_rotating.value = true
                canvas.value.rotate_lines(e)
            }
            else if (e.button == MOUSE_BUTTONS.LEFT_CLICK) {
                line_panning.value = true
                canvas.value.pan_lines(e)
            }
            else if (e.button == MOUSE_BUTTONS.RIGHT_CLICK) {
                line_spreading.value = true
                canvas.value.spread_lines(e)
            }
        }
        else if (map_store.state == STATE.EDIT_LINES) {
            if (map_store.line_point_placed) {
                let cursor_pos = get_mouse_pos({ x: e.clientX, y: e.clientY }, container.value)
                let a = canvas.value.from_rel_coords_to_canvas_pos(
                    map_store.lines
                    [map_store.current_region_ind]
                    [map_store.current_line_ind]
                    [map_store.current_line_point_ind]
                )
                let b = canvas.value.from_rel_coords_to_canvas_pos(
                    map_store.lines
                    [map_store.current_region_ind]
                    [map_store.current_line_ind]
                    [map_store.current_line_point_ind + 1]
                )
                
                // Check if line close to an existing point. Set point as current point.
                let MIN_DIST_POINT = 3
                let cursor_close_to_point = false
                if (get_distance(cursor_pos, a) <= MIN_DIST_POINT) {
                    cursor_close_to_point = true
                }
                if (get_distance(cursor_pos, b) <= MIN_DIST_POINT) {
                    map_store.current_line_point_ind += 1
                    cursor_close_to_point = true
                }
                if (e.button == MOUSE_BUTTONS.LEFT_CLICK) {
                    let canvas_region = get_region_canvas_coordinates(map_store.regions[map_store.current_region_ind])
                    // Start edition only if point in polygon
                    if (is_point_in_polygon(cursor_pos, canvas_region)) {
                        map_store.line_point_dragged = true
                        if (!cursor_close_to_point) {
                            // Create a new point and set it as the current point
                            let point_pos = get_map_coords(
                                map_store.coords, map_store.offset_display,
                                cursor_pos
                            )
                            map_store.lines
                                [map_store.current_region_ind]
                                [map_store.current_line_ind]
                                .splice(map_store.current_line_point_ind + 1, 0, point_pos)
                            map_store.lines_highlighted[map_store.current_region_ind] = [
                                map_store.lines[map_store.current_region_ind][map_store.current_line_ind]
                            ]
                            map_store.current_line_point_ind += 1
                        }
                    }
                }
                else if (e.button == MOUSE_BUTTONS.RIGHT_CLICK) {
                    // Delete point if cursor close to one. If the line has less than 2 points, delete the line.
                    if (cursor_close_to_point) {
                        map_store.lines
                            [map_store.current_region_ind]
                            [map_store.current_line_ind]
                            .splice(map_store.current_line_point_ind, 1)
                    }
                }
            }
            canvas.value.draw()
        }
        else if (map_store.state == STATE.ADD_LINE) {
            if (e.button == MOUSE_BUTTONS.LEFT_CLICK) {
                let cursor_pos = get_mouse_pos({ x: e.clientX, y: e.clientY }, container.value)
                let canvas_region = get_region_canvas_coordinates(map_store.regions[map_store.current_region_ind])
                if (is_point_in_polygon(cursor_pos, canvas_region)) {
                    let point_pos = get_map_coords(
                        map_store.coords, map_store.offset_display,
                        cursor_pos
                    )
                    if (!map_store.line_point_placed) {
                        // Add a new line
                        map_store.lines[map_store.current_region_ind].push([ point_pos ])
                        map_store.current_line_ind = map_store.lines[map_store.current_region_ind].length - 1
                        map_store.lines_highlighted[map_store.current_region_ind]
                            = [ map_store.lines[map_store.current_region_ind][map_store.current_line_ind] ]
                        map_store.line_point_placed = true
                    }
                    else {
                        // Add new point to line
                        map_store.lines[map_store.current_region_ind][map_store.current_line_ind].push(point_pos)
                        map_store.lines_highlighted[map_store.current_region_ind]
                            = [ map_store.lines[map_store.current_region_ind][map_store.current_line_ind] ]
                    }
                    canvas.value.draw()
                }
            }
            else if (e.button == MOUSE_BUTTONS.RIGHT_CLICK) {
                end_line_addition()
            }
        }
        else if (map_store.state == STATE.REMOVE_LINE) {
            if (map_store.current_line_ind != -1) {
                map_store.lines_highlighted[map_store.current_region_ind] = []
                map_store.lines[map_store.current_region_ind].splice(map_store.current_line_ind, 1)
                canvas.value.draw()
            }
        }
        else if (map_store.state == STATE.DISPLAY_VINEYARD) {
            if (e.button == MOUSE_BUTTONS.LEFT_CLICK || e.button == MOUSE_BUTTONS.MIDDLE_CLICK) {
                map_panning.value = true
                display.value.start_panning(e)
            }
            canvas.value.draw()
        }
        else if (map_store.state == STATE.SELECT_LINES) {
            if (e.button == MOUSE_BUTTONS.LEFT_CLICK) {
                map_store.selecting_zone = true
                map_store.zone_selection.start = get_mouse_pos({ x: e.clientX, y: e.clientY }, container.value)
                map_store.zone_selection.end = map_store.zone_selection.start
            }
            canvas.value.draw()
        }
    }

    const mouseup = () => { end_interaction() }
    const mouseleave = () => { end_interaction() }

    const mousewheel = (e) => {
        e.preventDefault()
        if (map_store.state == STATE.ADD_PLOT_SECTION
                || map_store.state == STATE.EDIT_LINES
                || map_store.state == STATE.ADD_LINE
                || map_store.state == STATE.REMOVE_LINE
                || map_store.state == STATE.DISPLAY_VINEYARD) {
            let display_nav_coords = display.value.zoom(e)
            map_store.coords = display_nav_coords.coords
            map_store.offset_display = display_nav_coords.offset_display
            store_coords_cookie()
            canvas.value.draw()
        }
    }

    const end_interaction = () => {
        map_panning.value = false
        line_panning.value = false
        line_spreading.value = false
        line_rotating.value = false
        if (map_store.selecting_zone) {
            map_store.selecting_zone = false
            canvas.value.draw()
        }
        map_store.line_point_dragged = false
        if (map_store.state == STATE.EDIT_LINES) {
            map_store.lines_highlighted[map_store.current_region_ind] = []
            canvas.value.draw()
        }
    }

    const end_line_addition = () => {
        if (!map_store.line_point_placed)
            return
        // Delete line if less than 2 points
        if (map_store.lines[map_store.current_region_ind][map_store.current_line_ind].length < 2) {
            map_store.lines[map_store.current_region_ind].splice(map_store.current_line_ind, 1)
        }
        map_store.lines_highlighted[map_store.current_region_ind] = []
        map_store.line_point_placed = false
        map_store.current_line_ind = -1
        map_store.line_point_placed = false
    }

    const add_point_to_region = () => {
        let new_point = from_rel_coords_to_mercator(map_store.cursor_rel_coords.x, map_store.cursor_rel_coords.y)
        if (check_intersection_polygon(map_store.regions[map_store.current_region_ind], new_point)) {
            map_store.regions[map_store.current_region_ind] = []
        }
        else {
            map_store.regions[map_store.current_region_ind].push(new_point)
        }
    }

    const finish_region = () => {
        if (check_intersection_polygon(map_store.regions[map_store.current_region_ind].slice(1), map_store.regions[map_store.current_region_ind][0])) {
            console.log("Region polygon is self-intersecting")
            map_store.regions[map_store.current_region_ind] = []
        }
        else if (map_store.regions[map_store.current_region_ind].length <= 2) {
            map_store.regions[map_store.current_region_ind] = []
        }
        else {
            map_store.regions[map_store.current_region_ind].push(map_store.regions[map_store.current_region_ind][0])
            map_store.state = STATE.EDIT_LINES_GLOBAL_PLACEMENT
            map_store.lines[map_store.current_region_ind] = []
            // Center map display on region
            center_map_on_region(map_store.regions[map_store.current_region_ind])
            canvas.value.compute_lines()
        }
    }

    const center_map_on_region = (region) => {
        let center_params = get_region_center_params(region, [ nb_tiles_x.value, nb_tiles_y.value ])
        if (map_store.state == STATE.EDIT_LINES_GLOBAL_PLACEMENT) {
            canvas.value.set_line_cursor(center_params.pos)
        }
        let display_nav_coords = display.value.position_map(center_params.pos, center_params.zoom, { x: 0.5, y: 0.5 })
        map_store.coords = display_nav_coords.coords
        map_store.offset_display = display_nav_coords.offset_display
        store_coords_cookie()
        canvas.value.draw()
    }

    const update_line_selection = (event) => {
        map_store.zone_selection.end = get_mouse_pos({ x: event.clientX, y: event.clientY }, container.value)
        map_store.lines_highlighted = []
        let rect = [
            { x: map_store.zone_selection.start.x, y: map_store.zone_selection.start.y },
            { x: map_store.zone_selection.start.x, y: map_store.zone_selection.end.y },
            { x: map_store.zone_selection.end.x, y: map_store.zone_selection.end.y },
            { x: map_store.zone_selection.end.x, y: map_store.zone_selection.start.y },
        ]
        for (let line of map_store.lines) {
            let line_already_done = false
            for (let line_done of map_store.lines_done) {
                if (line.id == line_done.id) {
                    line_already_done = true
                    break
                }
            }
            if (line_already_done)
                continue
            let line_start = canvas.value.from_mercator_to_canvas_pos(line.start)
            let line_end = canvas.value.from_mercator_to_canvas_pos(line.end)
            if (does_segment_intersect_rectangle(rect, [ line_start, line_end ]))
                map_store.lines_highlighted.push(line)
        }
    }

    const redraw = () => { canvas.value.draw() }

    watch(() => map_store.state, (new_state, old_state) => {
        map_store.line_point_placed = false
        if (new_state == STATE.EDIT_LINES_GLOBAL_PLACEMENT) {
            map_store.lines[map_store.current_region_ind] = []
            // Center map display on region
            center_map_on_region(map_store.regions[map_store.current_region_ind])
            canvas.value.compute_lines()
        }
        else if (new_state == STATE.EDIT_LINES || new_state == STATE.ADD_LINE || new_state == STATE.REMOVE_LINE) {
            canvas.value.set_line_cursor(null)
            map_store.current_line_ind
        }
        canvas.value.draw()
    })

    defineExpose({
        center_map_on_region,
        redraw
    })

</script>