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
        from_rel_coords_to_mercator,
        get_map_coords
    } from '../lib/map_navigation'
    import {
        check_intersection_polygon,
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

    onMounted(() => {
        let dims = get_dims_map(nb_tiles_x.value, nb_tiles_y.value)
        container.value.style["width"] = dims.width + "px"
        container.value.style["height"] = dims.height + "px"
        canvas.value.draw()
    })

    const mousemove = (e) => {
        e.preventDefault()
        map_store.cursor_rel_coords = get_map_coords(map_store.coords, map_store.offset_display, [ e.clientX, e.clientY ], container.value)
        if (map_panning.value) {
            let display_nav_coords = display.value.pan(e)
            map_store.coords = display_nav_coords.coords
            map_store.offset_display = display_nav_coords.offset_display
        }
        else if (map_store.line_panning)    canvas.value.pan_lines(e)
        else if (map_store.line_rotating)   canvas.value.rotate_lines(e)
        else if (map_store.line_spreading)  canvas.value.spread_lines(e)
        canvas.value.draw()
    }

    const mousedown = (e) => {
        e.preventDefault()
        if (map_store.state == STATE.SELECT_REGION) {
            if (e.button == MOUSE_BUTTONS.LEFT_CLICK)
                add_point_to_region()
            else if (e.button == MOUSE_BUTTONS.MIDDLE_CLICK) {
                display.value.start_panning(e)
                map_panning.value = true
            }
            else if (e.button == MOUSE_BUTTONS.RIGHT_CLICK)
                finish_region()
        }
        else if (map_store.state == STATE.PLACE_LINES) {
            if (e.button == MOUSE_BUTTONS.LEFT_CLICK && (e.shiftKey || e.ctrlKey)) {
                canvas.value.start_line_rotating()
                canvas.value.rotate_lines(e)
            }
            else if (e.button == MOUSE_BUTTONS.LEFT_CLICK) {
                canvas.value.start_line_panning()
                canvas.value.pan_lines(e)
            }
            else if (e.button == MOUSE_BUTTONS.RIGHT_CLICK) {
                canvas.value.start_line_spreading()
                canvas.value.spread_lines(e)
            }
        }
        else if (map_store.state == STATE.DISPLAY_VINEYARD) {
            if (e.button == MOUSE_BUTTONS.LEFT_CLICK || e.button == MOUSE_BUTTONS.MIDDLE_CLICK) {
                display.value.start_panning(e)
                map_panning.value = true
            }
        }
        canvas.value.draw()
    }

    const mouseup = () => {
        map_panning.value = false
        canvas.value.stop_line_panning()
        canvas.value.stop_line_rotating()
        canvas.value.stop_line_spreading()
    }

    const mouseleave = () => {
        map_panning.value = false
        canvas.value.stop_line_panning()
        canvas.value.stop_line_rotating()
        canvas.value.stop_line_spreading()
    }

    const mousewheel = (e) => {
        e.preventDefault()
        if (map_store.state == STATE.SELECT_REGION || map_store.state == STATE.DISPLAY_VINEYARD) {
            let display_nav_coords = display.value.zoom(e)
            map_store.coords = display_nav_coords.coords
            map_store.offset_display = display_nav_coords.offset_display
            canvas.value.draw()
        }
    }

    const add_point_to_region = () => {
        let new_point = from_rel_coords_to_mercator(map_store.cursor_rel_coords.x, map_store.cursor_rel_coords.y)
        if (check_intersection_polygon(map_store.regions.at(-1), new_point)) {
            map_store.regions = [ [] ]
        }
        else {
            map_store.regions.at(-1).push(new_point)
        }
    }

    const finish_region = () => {
        if (check_intersection_polygon(map_store.regions.at(-1).slice(1), map_store.regions.at(-1)[0])) {
            console.log("Region polygon is self-intersecting")
            map_store.regions = [ [] ]
        }
        else if (map_store.regions.at(-1).length <= 2) {
            map_store.regions = [ [] ]
        }
        else {
            map_store.regions.at(-1).push(map_store.regions.at(-1)[0])
            map_store.state = STATE.PLACE_LINES
            // Center map display on region
            center_map_on_region(map_store.regions.at(-1))
            canvas.value.compute_lines()
        }
    }

    const center_map_on_region = (region) => {
        let center_params = get_region_center_params(region, [ nb_tiles_x.value, nb_tiles_y.value ])
        if (map_store.state == STATE.PLACE_LINES) {
            canvas.value.set_line_cursor(center_params.pos)
        }
        let display_nav_coords = display.value.position_map(center_params.pos, center_params.zoom, { x: 0.5, y: 0.5 })
        map_store.coords = display_nav_coords.coords
        map_store.offset_display = display_nav_coords.offset_display
        canvas.value.draw()
    }

    const redraw = () => { canvas.value.draw() }

    defineExpose({
        center_map_on_region,
        redraw
    })

</script>