<script setup>
    import { reactive, ref, onMounted } from 'vue'

    const TILE_SIZE = 256
    const TILES_X = 3 // Number of tiles to show on the X axis
    const TILES_Y = 2

    const Z_MIN = 3
    const Z_MAX = 21

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
        if (tile.coords.x < coords.x || tile.coords.x > (coords.x + TILES_X)
                || tile.coords.y < coords.y || tile.coords.y > (coords.y + TILES_Y)) {
            return
        }
        let rel_x = tile.coords.x - coords.x
        let rel_y = tile.coords.y - coords.y
        let grid_ind = (rel_y) * (TILES_X + 1) + rel_x
        map_url.value[grid_ind] = tile.url
    }

    const map_grid = []

    const load_map = () => {
        // Update map grid
        let ind_x, ind_y
        for (let ind = 0; ind < (TILES_X + 1) * (TILES_Y + 1); ind++) {
            ind_x = ind % (TILES_X + 1)
            ind_y = Math.floor(ind / (TILES_X + 1))
            map_grid[ind] = [ coords.x + ind_x, coords.y + ind_y ]
        }
        // Load tiles
        map_grid.forEach((el) => {
            get_tile(el[0], el[1], coords.z).then(tile => set_tile(tile))
            .catch((error) => {
                console.log(error)
            })
        })
    }

    onMounted(() => {
        map_canvas.value.style["width"] = (TILE_SIZE * TILES_X) + "px"
        map_canvas.value.style["height"] = (TILE_SIZE * TILES_Y) + "px"
        let template_columns = ""
        for (let i = 0; i < TILES_X + 1; i++) {
            template_columns += "auto "
        }
        map_canvas.value.style["grid-template-columns"] = template_columns
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
            let i, j
            if (scroll_x < 0 && (coords.x - 1) >= 0) {
                shift_x = -1
                coords.x -= 1
                // shift tiles to the right
                for (i = 0; i < TILES_Y + 1; i++) {
                    for (j = (TILES_X + 1) * (i + 1) - 1; j > i * (TILES_X + 1); j--) {
                        map_url.value[j] = map_url.value[j - 1]
                    }
                }
            }
            else if (scroll_x > TILE_SIZE && (coords.x + (TILES_X + 1)) < max_ind) {
                shift_x = 1
                coords.x += 1
                // shift tiles to the left
                for (i = 0; i < TILES_Y + 1; i++) {
                    for (j = i * (TILES_X + 1); j < (TILES_X + 1) * (i + 1) - 1; j++) {
                        map_url.value[j] = map_url.value[j + 1]
                    }
                }
            }
            if (scroll_y < 0 && (coords.y - 1) >= 0) {
                shift_y = -1
                coords.y -= 1
                // shift tiles to the bottom
                for (i = 0; i < TILES_X + 1; i++) {
                    for (j = TILES_Y; j > 0; j--) {
                        map_url.value[j * (TILES_X + 1) + i] = map_url.value[(j - 1) * (TILES_X + 1) + i]
                    }
                }
            }
            else if (scroll_y > TILE_SIZE && (coords.y + (TILES_Y + 1)) < max_ind) {
                shift_y = 1
                coords.y += 1
                // shift tiles to the top
                for (i = 0; i < TILES_X + 1; i++) {
                    for (j = 0; j < TILES_Y; j++) {
                        map_url.value[j * (TILES_X + 1) + i] = map_url.value[(j + 1) * (TILES_X + 1) + i]
                    }
                }
            }
            if (shift_x == -1) {
                // load tiles at the left border
                for (i = 0; i < TILES_Y + 1; i++) {
                    get_tile(coords.x, coords.y + i, coords.z).then(tile => set_tile(tile))
                }
                scroll_x += TILE_SIZE
            }
            else if (shift_x == 1) {
                // load tiles at the right border
                for (i = 0; i < TILES_Y + 1; i++) {
                    get_tile(coords.x + TILES_X, coords.y + i, coords.z).then(tile => set_tile(tile))
                }
                scroll_x -= TILE_SIZE
            }
            if (shift_y == -1) {
                // load tiles at the top border
                for (i = 0; i < TILES_X + 1; i++) {
                    get_tile(coords.x + i, coords.y, coords.z).then(tile => set_tile(tile))
                }
                scroll_y += TILE_SIZE
            }
            else if (shift_y == 1) {
                // load tiles at the bottom border
                for (i = 0; i < TILES_X + 1; i++) {
                    get_tile(coords.x + i, coords.y + TILES_Y, coords.z).then(tile => set_tile(tile))
                }
                scroll_y -= TILE_SIZE
            }
            canvas.scrollLeft = Math.min(scroll_x, TILE_SIZE)
            canvas.scrollTop = Math.min(scroll_y, TILE_SIZE)
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
        if (z < Z_MIN || z > Z_MAX)
            return
        let prev_z = coords.z
        coords.z = z
        let nb_prev_rows = Math.pow(2, prev_z)
        let nb_rows = Math.pow(2, coords.z)
        let mouse_x = e.clientX - map_canvas.value.offsetLeft
        let mouse_y = e.clientY - map_canvas.value.offsetTop
        // X
        let rel_x = (Math.floor(mouse_x / TILE_SIZE) + (coords.x + 1) + (((mouse_x % TILE_SIZE) - (TILE_SIZE - map_canvas.value.scrollLeft)) / TILE_SIZE)) / nb_prev_rows
        let rel_v_x = mouse_x / (TILES_X * TILE_SIZE)
        let pos_x = rel_x * nb_rows
        let pos_left = pos_x - rel_v_x * TILES_X
        let e_pos_left = Math.floor(pos_left)
        let dec_pos_left = pos_left - e_pos_left
        coords.x = e_pos_left
        map_canvas.value.scrollLeft = dec_pos_left * TILE_SIZE
        // Y
        let rel_y = (Math.floor(mouse_y / TILE_SIZE) + (coords.y + 1) + (((mouse_y % TILE_SIZE) - (TILE_SIZE - map_canvas.value.scrollTop)) / TILE_SIZE)) / nb_prev_rows
        let rel_v_y = mouse_y / (TILES_Y * TILE_SIZE)
        let pos_y = rel_y * nb_rows
        let pos_top = pos_y - rel_v_y * TILES_Y
        let e_pos_top = Math.floor(pos_top)
        let dec_pos_top = pos_top - e_pos_top
        coords.y = e_pos_top
        map_canvas.value.scrollTop = dec_pos_top * TILE_SIZE
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
        /*width: 768px;
        height: 512px;*/
        overflow:hidden;
        display: grid;
        /*https://www.w3schools.com/css/tryit.asp?filename=trycss_grid_display_inline-grid*/
        /*grid-template-columns: auto auto auto auto;*/
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
            <img v-for="ind in (TILES_X + 1) * (TILES_Y + 1)" :src="map_url[ind - 1]">
        </div>
        <p>{{ "x= " + coords.x + " y= " + coords.y + " z= " + coords.z }}</p>
    </div>
</template>