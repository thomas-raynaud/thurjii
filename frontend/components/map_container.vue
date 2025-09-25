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
    import { useTemplateRef, ref, onMounted } from 'vue'

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
    } from '../lib/geometry'
    import { map_store } from '../stores/map_store'
    import { STATE, MOUSE_BUTTONS } from '../lib/enums'

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
    const region_point_dragged = ref(-1)
    const line_point_dragged = ref(-1)

    onMounted(() => {
        let dims = get_dims_map(nb_tiles_x.value, nb_tiles_y.value)
        container.value.style["width"] = dims.width + "px"
        container.value.style["height"] = dims.height + "px"
        map_store.selecting_zone = false
        canvas.value.draw()
    })

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
        if (region_point_dragged.value != -1) {
            // Change region point position
            let current_region = map_store.regions[map_store.current_region_ind][region_point_dragged.value]
            let edited_point = from_rel_coords_to_mercator(map_store.cursor_rel_coords.x, map_store.cursor_rel_coords.y)
            let updated_region = [ ...current_region ]
            updated_region[map_store.current_region_ind] = edited_point
            if (!check_intersection_polygon(updated_region, edited_point)) {
                map_store.regions[map_store.current_region_ind] = updated_region
                let region_change = [
                    updated_region[(map_store.current_region_ind - 1) < 0 ? (updated_region.length - 1) : (map_store.current_region_ind - 1)],
                    updated_region[map_store.current_region_ind],
                    updated_region[(map_store.current_region_ind + 1) % updated_region.length],
                ]
                for (let i = 0; i < map_store.lines.length; i++) {
                    let line = map_store.lines[i]
                    for (let j = 0; j < line.length - 1; j++) {
                        let l1 = line[j]
                        let l2 = line[j + 1]
                        
                        for (let k = 0; k < region_change.length - 1; i++) {
                            let c = from_mercator_to_canvas_pos(last_region[i])
                            let d = from_mercator_to_canvas_pos(last_region[(i + 1)])
                            let intersection = get_lines_intersection_point(p0t, p2t, c, d)
                        }
                        if (
                            intersection.x != Number.MAX_VALUE
                            && intersection.x >= Math.min(c.x, d.x)
                            && intersection.x <= Math.max(c.x, d.x)
                            && intersection.y >= Math.min(c.y, d.y)
                            && intersection.y <= Math.max(c.y, d.y)
                        ) {
                            // TODO
                        }
                    }
                    map_store.regions[map_store.current_region_ind][region_point_dragged.value] = edited_point
                }
            }
            canvas.value.draw()
        }
        if (line_point_dragged.value != -1) {
            //TODO: change line point position
            canvas.value.draw()
        }
    }

    const mousedown = (e) => {
        e.preventDefault()
        if (map_store.state == STATE.ADD_PLOT_SECTION) {
            if (e.button == MOUSE_BUTTONS.LEFT_CLICK)
                add_point_to_region()
            else if (e.button == MOUSE_BUTTONS.MIDDLE_CLICK) {
                display.value.start_panning(e)
                map_panning.value = true
            }
            else if (e.button == MOUSE_BUTTONS.RIGHT_CLICK)
                finish_region()
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
        else if (map_store.state == STATE.DISPLAY_VINEYARD) {
            if (e.button == MOUSE_BUTTONS.LEFT_CLICK || e.button == MOUSE_BUTTONS.MIDDLE_CLICK) {
                map_panning.value = true
                display.value.start_panning(e)
            }
        }
        else if (map_store.state == STATE.SELECT_LINES) {
            if (e.button == MOUSE_BUTTONS.LEFT_CLICK) {
                map_store.selecting_zone = true
                map_store.zone_selection.start = get_mouse_pos({ x: e.clientX, y: e.clientY }, container.value)
                map_store.zone_selection.end = map_store.zone_selection.start
            }
        }
        canvas.value.draw()
    }

    const mouseup = () => {
        map_panning.value = false
        line_panning.value = false
        line_spreading.value = false
        line_rotating.value = false
        if (map_store.selecting_zone) {
            map_store.selecting_zone = false
            canvas.value.draw()
        }
    }

    const mouseleave = () => {
        map_panning.value = false
        line_panning.value = false
        line_spreading.value = false
        line_rotating.value = false
        if (map_store.selecting_zone) {
            map_store.selecting_zone = false
            canvas.value.draw()
        }
    }

    const mousewheel = (e) => {
        e.preventDefault()
        if (map_store.state == STATE.ADD_PLOT_SECTION || map_store.state == STATE.DISPLAY_VINEYARD) {
            let display_nav_coords = display.value.zoom(e)
            map_store.coords = display_nav_coords.coords
            map_store.offset_display = display_nav_coords.offset_display
            canvas.value.draw()
        }
    }

    const add_point_to_region = () => {
        let new_point = from_rel_coords_to_mercator(map_store.cursor_rel_coords.x, map_store.cursor_rel_coords.y)
        if (check_intersection_polygon(map_store.regions[map_store.current_region_ind], new_point)) {
            map_store.regions = [ [] ]
        }
        else {
            map_store.regions[map_store.current_region_ind].push(new_point)
        }
    }

    const finish_region = () => {
        if (check_intersection_polygon(map_store.regions[map_store.current_region_ind].slice(1), map_store.regions[map_store.current_region_ind][0])) {
            console.log("Region polygon is self-intersecting")
            map_store.regions = [ [] ]
        }
        else if (map_store.regions[map_store.current_region_ind].length <= 2) {
            map_store.regions = [ [] ]
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

    defineExpose({
        center_map_on_region,
        redraw
    })

</script>