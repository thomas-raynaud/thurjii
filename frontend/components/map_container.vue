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
            @position-map="(pos, zoom, vp_coords) => { display.position_map(pos, zoom, vp_coords) }"
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
    import { get_dims_map } from '../lib/map_navigation'
    import { map_store } from '../stores/map_store'

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
        display.value.mousemove(e)
        if (map_store.state == 0 || map_store.panning)
            canvas.value.draw()
    }

    const mousedown = (e) => {
        e.preventDefault()
        if (e.button == 1)
            display.value.mousedown(e)
        else if (e.button == 0 || e.button == 2)
            canvas.value.mousedown(e)
    }

    const mouseup = () => {
        display.value.mouseup()
    }

    const mouseleave = () => {
        display.value.mouseleave()
    }

    const mousewheel = (e) => {
        e.preventDefault()
        display.value.zoom(e)
        canvas.value.draw()
    }
</script>