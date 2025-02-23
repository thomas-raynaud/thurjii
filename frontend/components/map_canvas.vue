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
        from_mercator_to_rel_coords,
        from_rel_coords_to_mercator,
        get_tile_size_from_zoom
    } from '../lib/map_navigation'
    import { check_intersection_polygon } from '../lib/geometry'
    import { map_store } from '../stores/map_store'

    const props = defineProps([ 'nbTilesX', 'nbTilesY' ])
    const nb_tiles_x = parseInt(props.nbTilesX)
    const nb_tiles_y = parseInt(props.nbTilesY)

    const canvas = useTemplateRef("canvas")

    let ctx
    let region = []
    let bounding_box = {
        start: { x: -1, y: -1},
        end: { x: -1, y: -1}
    }
    let line_cursor = {
        x: -1,
        y: -1
    }

    const emit = defineEmits([ 'positionMap' ])

    onMounted(() => {
        let dims = get_dims_map(nb_tiles_x, nb_tiles_y)
        canvas.value.style["width"] = dims.width + "px"
        canvas.value.style["height"] = dims.height + "px"
        canvas.value.width = dims.width
        canvas.value.height = dims.height
        ctx = canvas.value.getContext("2d")
        map_store.state = 0
        draw()
    })

    const mercator_to_canvas_pos = (mc) => {
        let rc = from_mercator_to_rel_coords(mc)
        return rel_coords_to_canvas_pos(rc)
    }

    const rel_coords_to_canvas_pos = (rc) => {
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

    const draw = () => {
        ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)
        if (region.length == 0)
            return
        let region_on_canvas = []
        for (let i = 0; i < region.length; i++) {
            region_on_canvas[i] = mercator_to_canvas_pos(region[i])
        }
        
        ctx.strokeStyle = 'red'
        ctx.lineWidth = '1'
        ctx.beginPath()
        let poly = new Path2D()
        ctx.moveTo(region_on_canvas[0].x, region_on_canvas[0].y)
        poly.moveTo(region_on_canvas[0].x, region_on_canvas[0].y)
        for (let i = 1; i < region.length; i++) {
            ctx.lineTo(region_on_canvas[i].x, region_on_canvas[i].y)
            poly.lineTo(region_on_canvas[i].x, region_on_canvas[i].y)
        }
        ctx.lineTo(region_on_canvas[0].x, region_on_canvas[0].y)
        poly.lineTo(region_on_canvas[0].x, region_on_canvas[0].y)
        poly.closePath()
        ctx.setLineDash([])
        ctx.stroke()
        let cursor_coords = rel_coords_to_canvas_pos(map_store.cursor_rel_coords)
        if (map_store.state == 0) {
            ctx.beginPath()
            ctx.setLineDash([1, 2])
            ctx.moveTo(region_on_canvas.at(-1).x, region_on_canvas.at(-1).y)
            ctx.lineTo(cursor_coords.x, cursor_coords.y)
            ctx.stroke()
        }
        ctx.fillStyle = "rgba(255, 0, 0, 0.25)"
        ctx.fill(poly, "evenodd")
        if (map_store.state == 0 && region.length >= 2) {
            let triangle_cursor = new Path2D()
            triangle_cursor.moveTo(region_on_canvas.at(-1).x, region_on_canvas.at(-1).y)
            triangle_cursor.lineTo(cursor_coords.x, cursor_coords.y)
            triangle_cursor.lineTo(region_on_canvas[0].x, region_on_canvas[0].y)
            triangle_cursor.closePath()
            ctx.fill(triangle_cursor, "evenodd")
        }
        if (map_store.state == 1) {
            // Compute bounding box
            let reg_start = mercator_to_canvas_pos(bounding_box.start)
            let reg_end = mercator_to_canvas_pos(bounding_box.end)
            let width = reg_end.x - reg_start.x
            let height = reg_end.y - reg_start.y
            ctx.beginPath()
            ctx.rect(reg_start.x, reg_start.y, width, height)
            ctx.fillStyle = "rgba(0, 0, 255, 0.25)"
            ctx.fill()
            // Show line cursor
            let line_cursor_canvas = rel_coords_to_canvas_pos(line_cursor)
            ctx.beginPath()
            ctx.arc(line_cursor_canvas.x, line_cursor_canvas.y, 4, 0, 2 * Math.PI)
            ctx.fillStyle = "black"
            ctx.fill()
            ctx.beginPath()
            ctx.arc(line_cursor_canvas.x, line_cursor_canvas.y, 2, 0, 2 * Math.PI)
            ctx.fillStyle = "white"
            ctx.fill()
            // Draw lines
            //let step = 10 // in pixels
        }
    }

    const mousedown = (e) => {
        if (e.button == 0) {
            if (map_store.state == 0) {
                let new_point = from_rel_coords_to_mercator(map_store.cursor_rel_coords.x, map_store.cursor_rel_coords.y)
                if (check_intersection_polygon(region, new_point)) {
                    region = []
                }
                else {
                    region.push(new_point)
                }
            }
        }
        else if (e.button == 2) {
            if (map_store.state == 0) {
                if (check_intersection_polygon(region.slice(1), region[0])) {
                    console.log("Region polygon is self-intersecting")
                    region = []
                }
                else if (region.length <= 2) {
                    region = []
                }
                else {
                    map_store.state = 1
                    // Compute bounding box
                    let region_min = { x: region[0].x, y: region[0].y }
                    let region_max = { x: region[0].x, y: region[0].y }
                    for (let i = 1; i < region.length; i++) {
                        region_min.x = Math.min(region_min.x, region[i].x)
                        region_min.y = Math.max(region_min.y, region[i].y)
                        region_max.x = Math.max(region_max.x, region[i].x)
                        region_max.y = Math.min(region_max.y, region[i].y)
                    }
                    bounding_box.start = region_min
                    bounding_box.end = region_max
                    // Center map display on boundary box
                    let bb_start = from_mercator_to_rel_coords(bounding_box.start)
                    let bb_end = from_mercator_to_rel_coords(bounding_box.end)
                    let width_bb = bb_end.x - bb_start.x
                    let height_bb = bb_end.y - bb_start.y
                    let zoom_x = -Math.log2((width_bb * 1.1) / nb_tiles_x)
                    let zoom_y = -Math.log2((height_bb * 1.1) / nb_tiles_y)
                    let zoom = Math.min(zoom_x, zoom_y)
                    line_cursor = { x: bb_start.x + width_bb / 2, y: bb_start.y + height_bb / 2 }
                    let vp_coords = { x: 0.5, y: 0.5 }
                    map_store.coords.z = zoom
                    emit('positionMap', line_cursor, zoom, vp_coords )
                }
            }
        }
        draw()
    }

    defineExpose({
        draw,
        mousedown
    })
</script>