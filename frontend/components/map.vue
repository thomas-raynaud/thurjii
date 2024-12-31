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
    const tile_timeout = 50

    const map_source = "https://mt0.google.com/vt/lyrs=s&hl=en&"

    const get_tile = (x, y, z) => {
        if(loading_tile.value == false) {
            loading_tile.value = true
            setTimeout(() => {loading_tile.value = false}, tile_timeout)
            return new Promise((resolve, reject) => {
                fetch(map_source + "x=" + x + "&y=" + y + "&z=" + z).then((image) => {
                    image.blob().then((blob) => {
                        resolve({
                            coords: { x: x, y: y, z: z },
                            url: URL.createObjectURL(blob)
                        })
                    })
                })
                .catch(error => {
                    if (z == 1) {
                        reject(error)
                    }
                    else {
                        reject(error) // tmp
                        // ... or load tile "above" (zoom - 1)
                        // and display it with these css attributes:
                        // transform: scale(200%) translate(64px, -64px);
                        // clip-path: rect(128px 128px auto auto);
                    }
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
            .catch((error) => {
                console.log(error)
            })
        })
    }

    onMounted(() => {
        load_map()
    })

    const pan = (e) => {
        if (map_selected.value && coords.z > 1) {
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

    const zoom = (e) => {
        e.preventDefault()
        let z = coords.z - 1
        if (e.deltaY < 0) {
            z = coords.z + 1
        }
        if (z < 1 || z > 21)
            return
        let prev_z = coords.z
        coords.z = z
        let nb_prev_rows = Math.pow(2, prev_z)
        let nb_rows = Math.pow(2, coords.z)
        let mouse_x = e.clientX - map_canvas.value.offsetLeft
        let mouse_y = e.clientY - map_canvas.value.offsetTop
        // X
        let rel_x = (Math.floor(mouse_x / 256) + (coords.x + 1) + (((mouse_x % 256) - (256 - map_canvas.value.scrollLeft)) / 256)) / nb_prev_rows
        let rel_v_x = mouse_x / 512
        let pos_x = rel_x * nb_rows
        let pos_left = pos_x - rel_v_x * 2
        let e_pos_left = Math.floor(pos_left)
        let dec_pos_left = pos_left - e_pos_left
        coords.x = e_pos_left
        map_canvas.value.scrollLeft = dec_pos_left * 256
        // Y
        let rel_y = (Math.floor(mouse_y / 256) + (coords.y + 1) + (((mouse_y % 256) - (256 - map_canvas.value.scrollTop)) / 256)) / nb_prev_rows
        let rel_v_y = mouse_y / 512
        let pos_y = rel_y * nb_rows
        let pos_top = pos_y - rel_v_y * 2
        let e_pos_top = Math.floor(pos_top)
        let dec_pos_top = pos_top - e_pos_top
        coords.y = e_pos_top
        map_canvas.value.scrollTop = dec_pos_top * 256
        if (coords.z == 1) {
            map_canvas.value.scrollLeft = 0
            map_canvas.value.scrollTop = 0
        }
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
        <div id="map-canvas" ref="map_canvas"
            @mousemove="pan"
            @mouseup="map_selected=false"
            @mousedown="map_mousedown"
            @mouseleave="map_selected=false"
            @wheel="zoom"
        >
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
        <p>{{ "x= " + coords.x + " y= " + coords.y + " z= " + coords.z }}</p>
    </div>
</template>