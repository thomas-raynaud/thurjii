<script setup>
    import { reactive, ref, onMounted } from 'vue'

    const coords = reactive({
        x: 0,
        y: 0,
        z: 3
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
    }

    const map_grid = []

    const load_map = () => {
        // Update map grid
        map_grid[0] = [ coords.x, coords.y ]
        map_grid[1] = [ coords.x + 1, coords.y ]
        map_grid[2] = [ coords.x + 2, coords.y ]
        map_grid[3] = [ coords.x, coords.y + 1 ]
        map_grid[4] = [ coords.x + 1, coords.y + 1 ]
        map_grid[5] = [ coords.x + 2, coords.y + 1 ]
        map_grid[6] = [ coords.x, coords.y + 2 ]
        map_grid[7] = [ coords.x + 1, coords.y + 2 ]
        map_grid[8] = [ coords.x + 2, coords.y + 2 ]
        // Load tiles
        map_grid.forEach((el) => {
            get_tile(el[0], el[1], coords.z).then(tile => set_tile(tile))
        })
    }

    onMounted(() => {
        load_map()
    })

    const pan = (e) => {
        if (map_selected.value) {
            e.preventDefault()
            const canvas = map_canvas.value
            let scroll_x = canvas.scrollLeft + (prev_x.value - e.clientX)
            let scroll_y = canvas.scrollTop + (prev_y.value - e.clientY)
            let max_ind = Math.pow(2, coords.z)
            let shift_x = 0
            let shift_y = 0
            if (scroll_x < 0 && (coords.x - 1) >= 0) {
                shift_x = -1
                coords.x -= 1
                // shift tiles to the right
                map_url.value[2] = map_url.value[1]
                map_url.value[1] = map_url.value[0]
                map_url.value[5] = map_url.value[4]
                map_url.value[4] = map_url.value[3]
                map_url.value[8] = map_url.value[7]
                map_url.value[7] = map_url.value[6]
            }
            else if (scroll_x > 256 && (coords.x + 3) < max_ind) {
                shift_x = 1
                coords.x += 1
                // shift tiles to the left
                map_url.value[0] = map_url.value[1]
                map_url.value[1] = map_url.value[2]
                map_url.value[3] = map_url.value[4]
                map_url.value[4] = map_url.value[5]
                map_url.value[6] = map_url.value[7]
                map_url.value[7] = map_url.value[8]
            }
            if (scroll_y < 0 && (coords.y - 1) >= 0) {
                shift_y = -1
                coords.y -= 1
                // shift tiles to the bottom
                map_url.value[6] = map_url.value[3]
                map_url.value[3] = map_url.value[0]
                map_url.value[7] = map_url.value[4]
                map_url.value[4] = map_url.value[1]
                map_url.value[8] = map_url.value[5]
                map_url.value[5] = map_url.value[2]
            }
            else if (scroll_y > 256 && (coords.y + 3) < max_ind) {
                shift_y = 1
                coords.y += 1
                // shift tiles to the top
                map_url.value[0] = map_url.value[3]
                map_url.value[3] = map_url.value[6]
                map_url.value[1] = map_url.value[4]
                map_url.value[4] = map_url.value[7]
                map_url.value[2] = map_url.value[5]
                map_url.value[5] = map_url.value[8]
            }
            if (shift_x == -1) {
                // load tiles at the left border
                get_tile(coords.x, coords.y, coords.z).then(tile => set_tile(tile))
                get_tile(coords.x, coords.y + 1, coords.z).then(tile => set_tile(tile))
                get_tile(coords.x, coords.y + 2, coords.z).then(tile => set_tile(tile))
                scroll_x += 256
            }
            else if (shift_x == 1) {
                // load tiles at the right border
                get_tile(coords.x + 2, coords.y, coords.z).then(tile => set_tile(tile))
                get_tile(coords.x + 2, coords.y + 1, coords.z).then(tile => set_tile(tile))
                get_tile(coords.x + 2, coords.y + 2, coords.z).then(tile => set_tile(tile))
                scroll_x -= 256
            }
            if (shift_y == -1) {
                // load tiles at the top border
                get_tile(coords.x, coords.y, coords.z).then(tile => set_tile(tile))
                get_tile(coords.x + 1, coords.y, coords.z).then(tile => set_tile(tile))
                get_tile(coords.x + 2, coords.y, coords.z).then(tile => set_tile(tile))
                scroll_y += 256
            }
            else if (shift_y == 1) {
                // load tiles at the bottom border
                get_tile(coords.x, coords.y + 2, coords.z).then(tile => set_tile(tile))
                get_tile(coords.x + 1, coords.y + 2, coords.z).then(tile => set_tile(tile))
                get_tile(coords.x + 2, coords.y + 2, coords.z).then(tile => set_tile(tile))
                scroll_y -= 256
            }
            canvas.scrollLeft = Math.min(scroll_x, 256)
            canvas.scrollTop = Math.min(scroll_y, 256)
            prev_x.value = e.clientX
            prev_y.value = e.clientY
        }
    }

    const zoom_in = () => {
        let prev_z = coords.z
        coords.z += 1
        let nb_prev_rows = Math.pow(2, prev_z)
        let nb_rows = Math.pow(2, coords.z)
        // X
        let rel_x = ((coords.x + 1) + (map_canvas.value.scrollLeft / 256)) / nb_prev_rows
        let pos_x = rel_x * nb_rows
        coords.x = Math.max(Math.floor(pos_x) - 1, 0)
        map_canvas.value.scrollLeft = Math.floor((pos_x - (coords.x + 1)) * 256)
        // Y
        let rel_y = ((coords.y + 1) + (map_canvas.value.scrollTop / 256)) / nb_prev_rows
        let pos_y = rel_y * nb_rows
        coords.y = Math.max(Math.floor(pos_y) - 1, 0)
        map_canvas.value.scrollTop = Math.floor((pos_y - (coords.y + 1)) * 256)        
        load_map()
    }

    const zoom_out = () => {
        coords.z -= 1
        load_map()
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
            <button @click="zoom_in()">Zoom in</button>
            <button @click="zoom_out()">Zoom out</button>
        </div>
        <p>{{ "x= " + coords.x + " y= " + coords.y + " z= " + coords.z }}</p>
    </div>
</template>