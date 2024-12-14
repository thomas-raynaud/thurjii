<script setup>
    import { reactive, computed, ref, onMounted } from 'vue'

    const coords = reactive({
        x: 0,
        y: 0,
        z: 1
    })

    const map_selected = ref(false)

    const prev_x = ref(0)
    const prev_y = ref(0)

    const map_canvas = ref(null)
    onMounted(() => {})

    const pan = (e) => {
        if (map_selected.value) {
            e.preventDefault()
            const canvas = map_canvas.value
            canvas.scrollLeft = canvas.scrollLeft + (prev_x.value - e.clientX)
            canvas.scrollTop = canvas.scrollTop + (prev_y.value - e.clientY)
            prev_x.value = e.clientX
            prev_y.value = e.clientY
        }
    }

    const map_mousedown = (e) => {
        e.preventDefault()
        prev_x.value = e.clientX
        prev_y.value = e.clientY
        map_selected.value = true
    }

    const map_url_top_left = computed(() => {
        return "https://mt0.google.com/vt/lyrs=s&hl=en&x=" + coords.x + "&y=" + coords.y + "&z=" + coords.z
    })
    const map_url_top_right = computed(() => {
        return "https://mt0.google.com/vt/lyrs=s&hl=en&x=" + (coords.x + 1) + "&y=" + coords.y + "&z=" + coords.z
    })
    const map_url_bottom_left = computed(() => {
        return "https://mt0.google.com/vt/lyrs=s&hl=en&x=" + coords.x + "&y=" + (coords.y + 1) + "&z=" + coords.z
    })
    const map_url_bottom_right = computed(() => {
        return "https://mt0.google.com/vt/lyrs=s&hl=en&x=" + (coords.x + 1) + "&y=" + (coords.y + 1) + "&z=" + coords.z
    })
</script>

<style scoped>
    #map-canvas {
        width: 200px;
        height: 200px;
        overflow:hidden;
        display: grid;
    }
</style>

<template>
    <div>
        <div id="map-canvas" ref="map_canvas" @mousemove="pan"@mouseup="map_selected=false" @mousedown="map_mousedown" @mouseleave="map_selected=false">
            <div>
                <img :src="map_url_top_left" />
                <img :src="map_url_top_right" />
            </div>
            <div>
                <img :src="map_url_bottom_left" />
                <img :src="map_url_bottom_right" />
            </div>
        </div>
        <button @click="coords.y = coords.y - 1">Up</button>
        <button @click="coords.y = coords.y + 1">Bottom</button>
        <button @click="coords.x = coords.x - 1">Left</button>
        <button @click="coords.x = coords.x + 1">Right</button>
        <button @click="coords.z = coords.z + 1">Zoom in</button>
        <button @click="coords.z = coords.z - 1">Zoom out</button>
        <p>{{ "x= " + coords.x + " y= " + coords.y + " z= " + coords.z }}</p>
    </div>
</template>