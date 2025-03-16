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
        margin: 0 10px;
    }
</style>

<script setup>
    import { useTemplateRef, ref, onMounted } from 'vue'

    import MapDisplay from './map_display.vue'
    import MapCanvas from './map_canvas.vue'
    import {
        get_dims_map,
        get_region_center_params,
        from_rel_coords_to_mercator
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

    onMounted(() => {
        let dims = get_dims_map(nb_tiles_x.value, nb_tiles_y.value)
        container.value.style["width"] = dims.width + "px"
        container.value.style["height"] = dims.height + "px"
        canvas.value.draw()
    })

    const mousemove = (e) => {
        e.preventDefault()
        display.value.update_cursor_coords(e)
        if (map_store.panning)              display.value.pan(e)
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
            else if (e.button == MOUSE_BUTTONS.MIDDLE_CLICK)
                display.value.start_panning(e)
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
        canvas.value.draw()
    }

    const mouseup = () => {
        display.value.stop_panning()
        canvas.value.stop_line_panning()
        canvas.value.stop_line_rotating()
        canvas.value.stop_line_spreading()
    }

    const mouseleave = () => {
        display.value.stop_panning()
        canvas.value.stop_line_panning()
        canvas.value.stop_line_rotating()
        canvas.value.stop_line_spreading()
    }

    const mousewheel = (e) => {
        e.preventDefault()
        if (map_store.state == STATE.SELECT_REGION) {
            display.value.zoom(e)
            canvas.value.draw()
        }
    }

    const add_point_to_region = () => {
        let new_point = from_rel_coords_to_mercator(map_store.cursor_rel_coords.x, map_store.cursor_rel_coords.y)
        if (check_intersection_polygon(map_store.region, new_point)) {
            map_store.region = []
        }
        else {
            map_store.region.push(new_point)
        }
    }

    const finish_region = () => {
        if (check_intersection_polygon(map_store.region.slice(1), map_store.region[0])) {
            console.log("Region polygon is self-intersecting")
            map_store.region = []
        }
        else if (map_store.region.length <= 2) {
            map_store.region = []
        }
        else {
            map_store.state = STATE.PLACE_LINES
            // Center map display on region
            center_map_on_region()
            compute_lines()
        }
    }

    const center_map_on_region = () => {
        let center_params = get_region_center_params(map_store.region, [ nb_tiles_x.value, nb_tiles_y.value ])
        if (map_store.state == STATE.PLACE_LINES) {
            canvas.value.set_line_cursor(center_params.pos)
        }
        map_store.coords.z = center_params.zoom
        display.value.position_map(center_params.pos, center_params.zoom, { x: 0.5, y: 0.5 })
    }

    defineExpose({
        center_map_on_region
    })

</script>