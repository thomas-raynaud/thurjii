<script setup>
    import { reactive, computed, ref, onMounted } from 'vue'

    const coords = reactive({
        x: 0,
        y: 0,
        z: 2
    })

    const map_selected = ref(false)

    const prev_x = ref(0)
    const prev_y = ref(0)

    const map_url = ref([])
    const map_canvas = ref(null)

    const loading_tile = ref(false)
    const tile_timeout = 200

    const map_source = "https://mt0.google.com/vt/lyrs=s&hl=en&"

    const get_tile = (x, y, z) => {
        let rel_x = x - coords.x
        let rel_y = y - coords.y
        let grid_ind = (rel_y) * 3 + rel_x
        map_grid_loaded[grid_ind] = false
        if(loading_tile.value == false) {
            loading_tile.value = true
            setTimeout(() => {loading_tile.value = false}, tile_timeout)
            return new Promise((resolve) => {
                fetch(map_source + "x=" + x + "&y=" + y + "&z=" + z).then((image) => {
                    image.blob().then((blob) => {
                        resolve({
                            coords: { x: x, y: y, z: z },
                            url: URL.createObjectURL(blob)
                        })
                    })
                })
            })
        }
        else {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve(get_tile(x, y, z))
                }, tile_timeout)
            })
        }
    }

    const set_tile = (tile) => {
        if (tile.coords.x < coords.x || tile.coords.x > coords.x + 2 
                || tile.coords.y < coords.y || tile.coords.y > coords.y + 2) {
            return
        }
        let rel_x = tile.coords.x - coords.x
        let rel_y = tile.coords.y - coords.y
        let grid_ind = (rel_y) * 3 + rel_x
        map_url.value[grid_ind] = tile.url
        map_grid_loaded[grid_ind] = true
    }

    const map_grid = [
        [ coords.x, coords.y ], [ coords.x + 1, coords.y ], [ coords.x + 2, coords.y ],
        [ coords.x, coords.y + 1 ], [ coords.x + 1, coords.y + 1 ], [ coords.x + 2, coords.y + 1 ],
        [ coords.x, coords.y + 2 ], [ coords.x + 1, coords.y + 2 ], [ coords.x + 2, coords.y + 2 ],
    ]

    const map_grid_loaded = [
        false, false, false,
        false, false, false,
        false, false, false
    ]

    onMounted(() => {
        map_grid.forEach((el) => {
            get_tile(el[0], el[1], coords.z).then(tile => set_tile(tile))
        })
        map_canvas.value.scrollLeft = 256
        map_canvas.value.scrollRight = 256
    })

    const pan = (e) => {
        if (map_selected.value) {
            e.preventDefault()
            const canvas = map_canvas.value
            let scroll_x = canvas.scrollLeft + (prev_x.value - e.clientX)
            let scroll_y = canvas.scrollTop + (prev_y.value - e.clientY)
            let max_ind = Math.pow(2, coords.z)
            if (scroll_x < 0 && (coords.x - 1) >= 0) {
                // shift tiles to the right
                if (map_grid_loaded[1]) map_url.value[2] = map_url.value[1]
                if (map_grid_loaded[0]) map_url.value[1] = map_url.value[0]
                if (map_grid_loaded[4]) map_url.value[5] = map_url.value[4]
                if (map_grid_loaded[3]) map_url.value[4] = map_url.value[3]
                if (map_grid_loaded[7]) map_url.value[8] = map_url.value[7]
                if (map_grid_loaded[6]) map_url.value[7] = map_url.value[6]
                // load tiles at the left border
                coords.x -= 1
                get_tile(coords.x, coords.y, coords.z).then(tile => set_tile(tile))
                get_tile(coords.x, coords.y + 1, coords.z).then(tile => set_tile(tile))
                get_tile(coords.x, coords.y + 2, coords.z).then(tile => set_tile(tile))
                scroll_x += 256
            }
            else if (scroll_x > 256 && (coords.x + 3) < max_ind) {
                // shift tiles to the left
                if (map_grid_loaded[1]) map_url.value[0] = map_url.value[1]
                if (map_grid_loaded[2]) map_url.value[1] = map_url.value[2]
                if (map_grid_loaded[4]) map_url.value[3] = map_url.value[4]
                if (map_grid_loaded[5]) map_url.value[4] = map_url.value[5]
                if (map_grid_loaded[7]) map_url.value[6] = map_url.value[7]
                if (map_grid_loaded[8]) map_url.value[7] = map_url.value[8]
                // load tiles at the right border
                coords.x += 1
                get_tile(coords.x + 2, coords.y, coords.z).then(tile => set_tile(tile))
                get_tile(coords.x + 2, coords.y + 1, coords.z).then(tile => set_tile(tile))
                get_tile(coords.x + 2, coords.y + 2, coords.z).then(tile => set_tile(tile))
                scroll_x -= 256
            }
            if (scroll_y < 0 && (coords.y - 1) >= 0) {
                // shift tiles to the bottom
                if (map_grid_loaded[3]) map_url.value[6] = map_url.value[3]
                if (map_grid_loaded[0]) map_url.value[3] = map_url.value[0]
                if (map_grid_loaded[4]) map_url.value[7] = map_url.value[4]
                if (map_grid_loaded[1]) map_url.value[4] = map_url.value[1]
                if (map_grid_loaded[5]) map_url.value[8] = map_url.value[5]
                if (map_grid_loaded[2]) map_url.value[5] = map_url.value[2]
                // load tiles at the top border
                coords.y -= 1
                get_tile(coords.x, coords.y, coords.z).then(tile => set_tile(tile))
                get_tile(coords.x + 1, coords.y, coords.z).then(tile => set_tile(tile))
                get_tile(coords.x + 2, coords.y, coords.z).then(tile => set_tile(tile))
                scroll_y += 256
            }
            else if (scroll_y > 256 && (coords.y + 3) < max_ind) {
                // shift tiles to the top
                if (map_grid_loaded[3]) map_url.value[0] = map_url.value[3]
                if (map_grid_loaded[6]) map_url.value[3] = map_url.value[6]
                if (map_grid_loaded[4]) map_url.value[1] = map_url.value[4]
                if (map_grid_loaded[7]) map_url.value[4] = map_url.value[7]
                if (map_grid_loaded[5]) map_url.value[2] = map_url.value[5]
                if (map_grid_loaded[8]) map_url.value[5] = map_url.value[8]
                // load tiles at the bottom border
                coords.y += 1
                get_tile(coords.x, coords.y + 2, coords.z).then(tile => set_tile(tile))
                get_tile(coords.x + 1, coords.y + 2, coords.z).then(tile => set_tile(tile))
                get_tile(coords.x + 2, coords.y + 2, coords.z).then(tile => set_tile(tile))
                scroll_y -= 256
            }
            canvas.scrollLeft = scroll_x
            canvas.scrollTop = scroll_y
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

    const TILE_SIZE = 256
    //https://developers.google.com/maps/documentation/tile/2d-tiles-overview
    //https://gis.stackexchange.com/questions/153839/how-to-transform-epsg3857-to-tile-pixel-coordinates-at-zoom-factor-0

    function fromMercatorToPoint(x, y) {
        return {
            x: TILE_SIZE * x, // TODO
            y: TILE_SIZE * y // TODO
        }
    }

    function fromMercatorToTileCoord(x, y, zoom) {
        let point = fromMercatorToPoint(x, y)
        let scale = Math.pow(2, zoom)

        return {
            x: Math.floor(point.x * scale / TILE_SIZE),
            y: Math.floor(point.y * scale / TILE_SIZE),
            z: zoom
        }
    }

    console.log(fromMercatorToTileCoord(544842, 5862290, 8))
</script>

<style scoped>
    #map-canvas {
        width: 512px;
        height: 512px;
        overflow:hidden;
        display: grid;
        /*https://www.w3schools.com/css/tryit.asp?filename=trycss_grid_display_inline-grid*/
        grid-template-columns: auto auto auto;
        padding: 0;
        margin: 0 10px;
    }

    #map-canvas img {
        width: 256px;
        height: 256px;
    }
</style>

<template>
    <div class="body row">
        <div id="map-canvas" ref="map_canvas" @mousemove="pan" @mouseup="map_selected=false" @mousedown="map_mousedown" @mouseleave="map_selected=false">
            <img :src="map_url[0]" />
            <img :src="map_url[1]" />
            <img :src="map_url[2]" />
            <img :src="map_url[3]" />
            <img :src="map_url[4]" />
            <img :src="map_url[5]" />
            <img :src="map_url[6]" />
            <img :src="map_url[7]" />
            <img :src="map_url[8]" />
        </div>
        <div>
            <button @click="coords.y = coords.y - 1">Up</button>
            <button @click="coords.y = coords.y + 1">Bottom</button>
            <button @click="coords.x = coords.x - 1">Left</button>
            <button @click="coords.x = coords.x + 1">Right</button>
            <button @click="coords.z = coords.z + 1">Zoom in</button>
            <button @click="coords.z = coords.z - 1">Zoom out</button>
        </div>
        <p>{{ "x= " + coords.x + " y= " + coords.y + " z= " + coords.z }}</p>
    </div>
</template>