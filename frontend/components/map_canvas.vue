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
    import { map_store } from '../stores/map_store'

    const props = defineProps([ 'nbTilesX', 'nbTilesY' ])
    const nb_tiles_x = parseInt(props.nbTilesX)
    const nb_tiles_y = parseInt(props.nbTilesY)

    const canvas = useTemplateRef("canvas")

    let line = [
        {
            x: -18755107.81,
            y: 9818379.08
        },
        {
            x: -4889152.04,
            y: 8375678.48
        }
    ]

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
        let line_on_canvas = []
        for (let i = 0; i < line.length; i++) {
            line_on_canvas[i] = mercator_to_canvas_pos(line[i])
        }
        let ctx = canvas.value.getContext("2d")
        ctx.clearRect(0, 0, canvas.value.width, canvas.value.height)
        ctx.beginPath()
        ctx.moveTo(line_on_canvas[0].x, line_on_canvas[0].y)
        for (let i = 1; i < line.length; i++) {
            ctx.lineTo(line_on_canvas[i].x, line_on_canvas[i].y)
        }
        ctx.strokeStyle = 'red'
        ctx.lineWidth = '1'
        ctx.stroke()
    }

    const mousedown = (e) => {
        line.push(from_rel_coords_to_mercator(map_store.cursor_rel_coords.x, map_store.cursor_rel_coords.y))
        draw()
    }

    defineExpose({
        draw,
        mousedown
    })
</script>