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
        TILE_SIZE,
        get_dims_map,
        from_mercator_to_rel_coords,
        from_rel_coords_to_mercator
    } from '../lib/map_navigation'
    import { check_intersection_polygon } from '../lib/geometry'
    import { map_store } from '../stores/map_store'

    const props = defineProps([ 'nbTilesX', 'nbTilesY' ])
    const nb_tiles_x = parseInt(props.nbTilesX)
    const nb_tiles_y = parseInt(props.nbTilesY)

    const canvas = useTemplateRef("canvas")

    let line = []

    onMounted(() => {
        let dims = get_dims_map(nb_tiles_x, nb_tiles_y)
        canvas.value.style["width"] = dims.width + "px"
        canvas.value.style["height"] = dims.height + "px"
        canvas.value.width = dims.width
        canvas.value.height = dims.height
        draw()
    })

    const mercator_to_canvas_pos = (mc) => {
        let rc = from_mercator_to_rel_coords(mc.x, mc.y)
        return rel_coords_to_canvas_pos(rc)
        
    }

    const rel_coords_to_canvas_pos = (rc) => {
        let tcx = rc.x * Math.pow(2, map_store.coords.z)
        let tcy = rc.y * Math.pow(2, map_store.coords.z)
        let pos_left = map_store.coords.x + (map_store.offset_display.x / TILE_SIZE)
        let pos_top = map_store.coords.y + (map_store.offset_display.y / TILE_SIZE)
        return {
            x: (tcx - pos_left) * TILE_SIZE,
            y: (tcy - pos_top) * TILE_SIZE
        }
    }

    const draw = () => {
        let ctx = canvas.value.getContext("2d")
        ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)
        if (line.length == 0)
            return
        let line_on_canvas = []
        for (let i = 0; i < line.length; i++) {
            line_on_canvas[i] = mercator_to_canvas_pos(line[i])
        }
        
        ctx.strokeStyle = 'red'
        ctx.lineWidth = '1'
        ctx.beginPath()
        let poly = new Path2D()
        ctx.moveTo(line_on_canvas[0].x, line_on_canvas[0].y)
        poly.moveTo(line_on_canvas[0].x, line_on_canvas[0].y)
        for (let i = 1; i < line.length; i++) {
            ctx.lineTo(line_on_canvas[i].x, line_on_canvas[i].y)
            poly.lineTo(line_on_canvas[i].x, line_on_canvas[i].y)
        }
        ctx.lineTo(line_on_canvas[0].x, line_on_canvas[0].y)
        poly.lineTo(line_on_canvas[0].x, line_on_canvas[0].y)
        ctx.setLineDash([])
        ctx.stroke()
        ctx.beginPath()
        ctx.setLineDash([1, 2])
        ctx.moveTo(line_on_canvas.at(-1).x, line_on_canvas.at(-1).y)
        let cursor_coords = rel_coords_to_canvas_pos(map_store.cursor_rel_coords)
        ctx.lineTo(cursor_coords.x, cursor_coords.y)
        ctx.stroke()
        poly.closePath()
        ctx.fillStyle = "rgba(255, 0, 0, 0.25)"
        ctx.fill(poly, "evenodd")
        if (line.length >= 2) {
            let triangle_cursor = new Path2D()
            triangle_cursor.moveTo(line_on_canvas.at(-1).x, line_on_canvas.at(-1).y)
            triangle_cursor.lineTo(cursor_coords.x, cursor_coords.y)
            triangle_cursor.lineTo(line_on_canvas[0].x, line_on_canvas[0].y)
            triangle_cursor.closePath()
            ctx.fill(triangle_cursor, "evenodd")
        }
    }

    const mousedown = (e) => {
        if (e.button == 0) {
            let new_point = from_rel_coords_to_mercator(map_store.cursor_rel_coords.x, map_store.cursor_rel_coords.y)
            if (check_intersection_polygon(line, new_point)) {
                line = []
            }
            else {
                line.push(new_point)
            }
        }
        else if (e.button == 2) {
            console.log(check_intersection_polygon(line.slice(1), line[0])) // true -> polygon incorrect
            line = []
        }
        draw()
    }

    defineExpose({
        draw,
        mousedown
    })
</script>