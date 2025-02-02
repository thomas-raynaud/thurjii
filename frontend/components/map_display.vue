<template>
    <div ref="display" class="map-display">
        <img v-for="ind in (nb_tiles_x + 1) * (nb_tiles_y + 1)" :src="tile_urls[ind - 1]">
    </div>
</template>

<style scoped>
    .map-display {
        position: absolute;
        overflow:hidden;
        display: grid;
    }

    .map-display img {
        width: 256px;
        height: 256px;
    }
</style>

<script setup>
    import { ref, useTemplateRef, onMounted } from 'vue'
    import { map_store } from '../stores/map_store'
    import { TILE_SIZE, get_dims_map, get_map_coords, get_viewport_coords } from '../lib/map_navigation'

    const Z_MIN = 3
    const Z_MAX = 21
    const TILE_TIMEOUT = 100
    const MAP_SOURCE = "https://mt0.google.com/vt/lyrs=s&hl=en&"

    let loading_tile = false
    let prev_x = 0
    let prev_y = 0

    const tile_urls = ref([])
    const display = useTemplateRef('display')

    const props = defineProps([ 'nbTilesX', 'nbTilesY' ])
    const nb_tiles_x = ref(parseInt(props.nbTilesX))
    const nb_tiles_y = ref(parseInt(props.nbTilesY))

    onMounted(() => {
        let dims = get_dims_map(nb_tiles_x.value, nb_tiles_y.value)
        display.value.style["width"] = dims.width + "px"
        display.value.style["height"] = dims.height + "px"
        let template_columns = ""
        for (let i = 0; i < nb_tiles_x.value + 1; i++) {
            template_columns += "auto "
        }
        display.value.style["grid-template-columns"] = template_columns
        map_store.panning = false
        let x = $cookies.get("coords_x")
        let y = $cookies.get("coords_y")
        let z = $cookies.get("coords_z")
        let offset_x = $cookies.get("offset_display_x")
        let offset_y = $cookies.get("offset_display_x")
        map_store.coords.x = (x == null ? 0 : parseInt(x))
        map_store.coords.y = (y == null ? 0 : parseInt(y))
        map_store.coords.z = (z == null ? 3 : parseInt(z))
        map_store.offset_display.x = (offset_x == null ? 0 : offset_x)
        map_store.offset_display.y = (offset_y == null ? 0 : offset_y)
        display.value.scrollLeft = map_store.offset_display.x
        display.value.scrollTop = map_store.offset_display.y
        load_map()
    })

    const store_coords_cookie = () => {
        $cookies.set("coords_x", map_store.coords.x)
        $cookies.set("coords_y", map_store.coords.y)
        $cookies.set("coords_z", map_store.coords.z)
        $cookies.set("offset_display_x", map_store.offset_display.x)
        $cookies.set("offset_display_y", map_store.offset_display.y)
    }

    const load_tile = (x, y, z) => {
        if (loading_tile) {
            return new Promise((resolve) => {
                setTimeout(() => {
                    resolve(load_tile(x, y, z))
                }, TILE_TIMEOUT)
            })
        }
        else {
            loading_tile = true
            setTimeout(() => { loading_tile = false }, TILE_TIMEOUT)
            return new Promise((resolve, reject) => {
                resolve()
                fetch(MAP_SOURCE + "x=" + x + "&y=" + y + "&z=" + z).then((image) => {
                    image.blob().then((blob) => {
                        if (x >= map_store.coords.x && x <= (nb_tiles_x.value + map_store.coords.x) &&
                            y >= map_store.coords.y && y <= (nb_tiles_y.value + map_store.coords.y)
                        ) {
                            let rel_x = x - map_store.coords.x
                            let rel_y = y - map_store.coords.y
                            let grid_ind = (rel_y) * (nb_tiles_x.value + 1) + rel_x
                            tile_urls.value[grid_ind] = URL.createObjectURL(blob)
                        }
                        resolve()
                    })
                })
                .catch(error => {
                    reject(error)
                    // ... or load tile "above" (zoom - 1)
                    // and display it with these css attributes:
                    // transform: scale(200%) translate(64px, -64px);
                    // clip-path: rect(128px 128px auto auto);
                })
            })
        }
    }

    const load_map = () => {
        // Update map grid
        let ind_x, ind_y
        let grid_coords = []
        for (let ind = 0; ind < (nb_tiles_x.value + 1) * (nb_tiles_y.value + 1); ind++) {
            ind_x = ind % (nb_tiles_x.value + 1)
            ind_y = Math.floor(ind / (nb_tiles_x.value + 1))
            grid_coords[ind] = [ map_store.coords.x + ind_x, map_store.coords.y + ind_y ]
        }
        // Load tiles
        grid_coords.forEach((el) => {
            load_tile(el[0], el[1], map_store.coords.z).catch((error) => { console.log(error) })
        })
    }

    const mousemove = (e) => {
        map_store.cursor_rel_coords = get_map_coords(map_store.coords, [ e.clientX, e.clientY ], display.value)
        map_store.cursor_rel_coords_rounded.x = Math.floor(map_store.cursor_rel_coords.x * 1000) / 1000
        map_store.cursor_rel_coords_rounded.y = Math.floor(map_store.cursor_rel_coords.y * 1000) / 1000
        if (map_store.panning)
            pan(e)
    }

    const mousedown = (e) => {
        prev_x = e.clientX
        prev_y = e.clientY
        map_store.panning = true
    }

    const mouseup    = () => { map_store.panning = false }
    const mouseleave = () => { map_store.panning = false }

    const pan = (e) => {
        let scroll_x = display.value.scrollLeft + (prev_x - e.clientX)
        let scroll_y = display.value.scrollTop + (prev_y - e.clientY)
        let max_ind = Math.pow(2, map_store.coords.z)
        let shift_x = 0
        let shift_y = 0
        let i, j
        if (scroll_x < 0 && (map_store.coords.x - 1) >= 0) {
            shift_x = -1
            map_store.coords.x -= 1
            // shift tiles to the right
            for (i = 0; i < nb_tiles_y.value + 1; i++) {
                for (j = (nb_tiles_x.value + 1) * (i + 1) - 1; j > i * (nb_tiles_x.value + 1); j--) {
                    tile_urls.value[j] = tile_urls.value[j - 1]
                }
            }
        }
        else if (scroll_x > TILE_SIZE && (map_store.coords.x + (nb_tiles_x.value + 1)) < max_ind) {
            shift_x = 1
            map_store.coords.x += 1
            // shift tiles to the left
            for (i = 0; i < nb_tiles_y.value + 1; i++) {
                for (j = i * (nb_tiles_x.value + 1); j < (nb_tiles_x.value + 1) * (i + 1) - 1; j++) {
                    tile_urls.value[j] = tile_urls.value[j + 1]
                }
            }
        }
        if (scroll_y < 0 && (map_store.coords.y - 1) >= 0) {
            shift_y = -1
            map_store.coords.y -= 1
            // shift tiles to the bottom
            for (i = 0; i < nb_tiles_x.value + 1; i++) {
                for (j = nb_tiles_y.value; j > 0; j--) {
                    tile_urls.value[j * (nb_tiles_x.value + 1) + i] = tile_urls.value[(j - 1) * (nb_tiles_x.value + 1) + i]
                }
            }
        }
        else if (scroll_y > TILE_SIZE && (map_store.coords.y + (nb_tiles_y.value + 1)) < max_ind) {
            shift_y = 1
            map_store.coords.y += 1
            // shift tiles to the top
            for (i = 0; i < nb_tiles_x.value + 1; i++) {
                for (j = 0; j < nb_tiles_y.value; j++) {
                    tile_urls.value[j * (nb_tiles_x.value + 1) + i] = tile_urls.value[(j + 1) * (nb_tiles_x.value + 1) + i]
                }
            }
        }
        if (shift_x == -1) {
            // load tiles at the left border
            for (i = 0; i < nb_tiles_y.value + 1; i++) {
                load_tile(map_store.coords.x, map_store.coords.y + i, map_store.coords.z)
            }
            scroll_x += TILE_SIZE
        }
        else if (shift_x == 1) {
            // load tiles at the right border
            for (i = 0; i < nb_tiles_y.value + 1; i++) {
                load_tile(map_store.coords.x + nb_tiles_x.value, map_store.coords.y + i, map_store.coords.z)
            }
            scroll_x -= TILE_SIZE
        }
        if (shift_y == -1) {
            // load tiles at the top border
            for (i = 0; i < nb_tiles_x.value + 1; i++) {
                load_tile(map_store.coords.x + i, map_store.coords.y, map_store.coords.z)
            }
            scroll_y += TILE_SIZE
        }
        else if (shift_y == 1) {
            // load tiles at the bottom border
            for (i = 0; i < nb_tiles_x.value + 1; i++) {
                load_tile(map_store.coords.x + i, map_store.coords.y + nb_tiles_y.value, map_store.coords.z)
            }
            scroll_y -= TILE_SIZE
        }
        map_store.offset_display.x = Math.min(scroll_x, TILE_SIZE)
        display.value.scrollLeft = map_store.offset_display.x
        map_store.offset_display.y = Math.min(scroll_y, TILE_SIZE)
        display.value.scrollTop = map_store.offset_display.y
        prev_x = e.clientX
        prev_y = e.clientY
        store_coords_cookie()
    }

    const zoom = (e) => {
        let z = map_store.coords.z - 1
        if (e.deltaY < 0) {
            z = map_store.coords.z + 1
        }
        if (z < Z_MIN || z > Z_MAX)
            return
        let nb_tiles_on_axis = Math.pow(2, z)
        let vp_coords = get_viewport_coords([ e.clientX, e.clientY ], display.value, [ nb_tiles_x.value, nb_tiles_y.value ])
        // X
        let pos_x = map_store.cursor_rel_coords.x * nb_tiles_on_axis
        let pos_left = pos_x - vp_coords.x * nb_tiles_x.value
        let e_pos_left = Math.floor(pos_left)
        let dec_pos_left = pos_left - e_pos_left
        map_store.coords.x = e_pos_left
        map_store.offset_display.x = dec_pos_left * TILE_SIZE
        display.value.scrollLeft = map_store.offset_display.x
        // Y
        let pos_y = map_store.cursor_rel_coords.y * nb_tiles_on_axis
        let pos_top = pos_y - vp_coords.y * nb_tiles_y.value
        let e_pos_top = Math.floor(pos_top)
        let dec_pos_top = pos_top - e_pos_top
        map_store.coords.y = e_pos_top
        map_store.offset_display.y = dec_pos_top * TILE_SIZE
        display.value.scrollTop = map_store.offset_display.y
        map_store.coords.z = z
        if (map_store.coords.z == 1) {
            display.value.scrollLeft = 0
            display.value.scrollTop = 0
        }
        store_coords_cookie()
        load_map()
    }

    defineExpose({
        mousemove, mousedown, mousedown, mouseleave, mouseup, zoom
    })
</script>