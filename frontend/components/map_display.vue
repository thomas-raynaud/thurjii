<script setup>
    const Z_MIN = 3
    const Z_MAX = 21

    const TILE_TIMEOUT = 50
    const MAP_SOURCE = "https://mt0.google.com/vt/lyrs=s&hl=en&"

    const map_url = ref([])
    const map_grid = []
    const map_selected = ref(false)
    const loading_tile = ref(false)

    defineProps(['width'])
    defineProps(['height'])

    onMounted(() => {
        let width_str = width + "px"
        let height_str = height + "px"
        map_display.value.style["width"] = width_str
        map_display.value.style["height"] = height_str
        let template_columns = ""
        for (let i = 0; i < TILES_X + 1; i++) {
            template_columns += "auto "
        }
        map_display.value.style["grid-template-columns"] = template_columns
    })
</script>

<style scoped>
    #map-display {
        position: absolute;
        overflow:hidden;
        display: grid;
    }

    #map-display img {
        width: 256px;
        height: 256px;
    }
</style>

<template>
    <div id="map-display" ref="map_display">
        <img v-for="ind in (TILES_X + 1) * (TILES_Y + 1)" :src="map_url[ind - 1]">
    </div>
</template>