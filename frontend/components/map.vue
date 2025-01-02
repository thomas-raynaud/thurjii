<script setup>
    import { reactive, computed, ref, onMounted } from 'vue'

    const TILE_SIZE = 256
    const TILES_X = 3 // Number of tiles to show on the X axis
    const TILES_Y = 2

    const Z_MIN = 3
    const Z_MAX = 21

    const TILE_TIMEOUT = 50
    const MAP_SOURCE = "https://mt0.google.com/vt/lyrs=s&hl=en&"

    const map_grid = []

    const coords = reactive({
        x: 0,
        y: 0,
        z: 3
    })

    const cursor_coords = reactive({
        x: 0,
        y: 0
    })

    const merc_cords = computed(() => {
        let m_coords = from_tile_coord_to_mercator(cursor_coords.x, cursor_coords.y, coords.z)
        return {
            x: Math.floor(m_coords.x * 100) / 100,
            y: Math.floor(m_coords.y * 100) / 100
        }
    })

    const map_selected = ref(false)

    const prev_x = ref(0)
    const prev_y = ref(0)

    const map_url = ref([])
    const map_container = ref(null)
    const map_display = ref(null)
    const map_canvas = ref(null)

    const loading_tile = ref(false)
    
    onMounted(() => {
        let width = (TILE_SIZE * TILES_X)
        let height = (TILE_SIZE * TILES_Y)
        let width_str = width + "px"
        let height_str = height + "px"
        map_container.value.style["width"] = width_str
        map_container.value.style["height"] = height_str
        map_display.value.style["width"] = width_str
        map_display.value.style["height"] = height_str
        map_canvas.value.style["width"] = width_str
        map_canvas.value.style["height"] = height_str
        map_canvas.value.width = width
        map_canvas.value.height = height
        let template_columns = ""
        for (let i = 0; i < TILES_X + 1; i++) {
            template_columns += "auto "
        }
        map_display.value.style["grid-template-columns"] = template_columns
        load_map()

        let ctx = map_canvas.value.getContext("2d")
        console.log(ctx)
        ctx.beginPath()
        ctx.moveTo(1, 1)
        ctx.lineTo(300, 300)
        ctx.strokeStyle = 'black'
        ctx.lineWidth = '2'
        ctx.stroke()
    })

    const get_tile = (x, y, z) => {
        if(loading_tile.value == false) {
            loading_tile.value = true
            setTimeout(() => {loading_tile.value = false}, TILE_TIMEOUT)
            return new Promise((resolve, reject) => {
                fetch(MAP_SOURCE + "x=" + x + "&y=" + y + "&z=" + z).then((image) => {
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
                        reject(error)
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
                }, TILE_TIMEOUT)
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

    const get_mouse_pos = (e) => {
        return {
            x: e.clientX + document.documentElement.scrollLeft - map_container.value.offsetLeft,
            y: e.clientY + document.documentElement.scrollTop - map_container.value.offsetTop
        }
    }

    const map_mousemove = (e) => {
        e.preventDefault()
        if (map_selected.value && coords.z > 1) {
            pan(e)
        }
        let map_coords = get_map_coords(e)
        cursor_coords.x = Math.floor(map_coords.x * 1000) / 1000
        cursor_coords.y = Math.floor(map_coords.y * 1000) / 1000
    }

    const pan = (e) => {
        const display = map_display.value
        let scroll_x = display.scrollLeft + (prev_x.value - e.clientX)
        let scroll_y = display.scrollTop + (prev_y.value - e.clientY)
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
        display.scrollLeft = Math.min(scroll_x, TILE_SIZE)
        display.scrollTop = Math.min(scroll_y, TILE_SIZE)
        prev_x.value = e.clientX
        prev_y.value = e.clientY
    }

    const get_map_coords = (e) => {
        let mouse_pos = get_mouse_pos(e)
        return {
            x: (Math.floor(mouse_pos.x / TILE_SIZE) + (coords.x + 1) + (((mouse_pos.x % TILE_SIZE) - (TILE_SIZE - map_display.value.scrollLeft)) / TILE_SIZE)) / Math.pow(2, coords.z),
            y: (Math.floor(mouse_pos.y / TILE_SIZE) + (coords.y + 1) + (((mouse_pos.y % TILE_SIZE) - (TILE_SIZE - map_display.value.scrollTop)) / TILE_SIZE)) / Math.pow(2, coords.z)
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
        let nb_rows = Math.pow(2, z)
        let rel_point = get_map_coords(e)
        let mouse_pos = get_mouse_pos(e)
        // X
        let rel_v_x = mouse_pos.x / (TILES_X * TILE_SIZE)
        let pos_x = rel_point.x * nb_rows
        let pos_left = pos_x - rel_v_x * TILES_X
        let e_pos_left = Math.floor(pos_left)
        let dec_pos_left = pos_left - e_pos_left
        coords.x = e_pos_left
        map_display.value.scrollLeft = dec_pos_left * TILE_SIZE
        // Y
        let rel_v_y = mouse_pos.y / (TILES_Y * TILE_SIZE)
        let pos_y = rel_point.y * nb_rows
        let pos_top = pos_y - rel_v_y * TILES_Y
        let e_pos_top = Math.floor(pos_top)
        let dec_pos_top = pos_top - e_pos_top
        coords.y = e_pos_top
        map_display.value.scrollTop = dec_pos_top * TILE_SIZE
        coords.z = z
        if (coords.z == 1) {
            map_display.value.scrollLeft = 0
            map_display.value.scrollTop = 0
        }
        load_map()
    }

    const map_mousedown = (e) => {
        e.preventDefault()
        prev_x.value = e.clientX
        prev_y.value = e.clientY
        map_selected.value = true
    }

    const from_tile_coord_to_mercator = (x, y, z) => {
        let equator = 40075016.68557849
        return {
            x: equator * ((x) - 0.5),
            y: equator * ((1 - y) - 0.5)
        }
    }

    const from_mercator_to_tile_coord = (x, y, z) => {
        let equator = 40075016.68557849
        return {
            x: ((x + (equator / 2)) / equator) * Math.pow(2, z),
            y: ((-y + (equator / 2)) / equator) * Math.pow(2, z)
        }
    }
</script>

<style scoped>
    #map-container {
        position: relative;
        padding: 0;
        margin: 0 10px;
    }

    #map-display {
        position: absolute;
        overflow:hidden;
        display: grid;
    }

    #map-display img {
        width: 256px;
        height: 256px;
    }

    #map-canvas {
        position: absolute;
        z-index: 1;
    }
</style>

<template>
    <div class="body row">
        <div id="map-container" ref="map_container"
                @mousemove="map_mousemove"
                @mouseup="map_selected=false"
                @mousedown="map_mousedown"
                @mouseleave="map_selected=false"
                @wheel="zoom">
            <div id="map-display" ref="map_display">
                <img v-for="ind in (TILES_X + 1) * (TILES_Y + 1)" :src="map_url[ind - 1]">
            </div>
            <canvas id="map-canvas" ref="map_canvas"></canvas>
        </div>
        <p>{{ "x= " + cursor_coords.x + " y= " + cursor_coords.y + " z= " + coords.z }}</p>
        <p>{{ "mx= " + merc_cords.x}}</p>
        <p>{{ "my= " + merc_cords.y}}</p>
    </div>
</template>