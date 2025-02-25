<template>
    <div
        ref="display" class="map-display"
        :style="{
            'grid-template-columns': Array(nb_tiles_x).fill('auto').join(' '),
            width: TILE_SIZE * nb_tiles_x_init + 'px',
            height: TILE_SIZE * nb_tiles_y_init + 'px'
        }"
    >
        <img
            v-for="ind in nb_tiles_x * nb_tiles_y"
            :src="tile_urls[ind - 1]"
            :style="{ width: tile_size + 'px', height: tile_size + 'px'}"
        />
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
    import { ref, useTemplateRef, onMounted, computed } from 'vue'
    import { map_store } from '../stores/map_store'
    import {
        TILE_SIZE,
        get_map_coords,
        get_nb_tiles_displayed,
        get_viewport_coords,
        get_tile_size_from_zoom
    } from '../lib/map_navigation'
    import { fix_decimal } from '../lib/math'

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
    const nb_tiles_x_init = ref(parseInt(props.nbTilesX))
    const nb_tiles_y_init = ref(parseInt(props.nbTilesY))

    const nb_tiles_x = computed(() => {
        let map_width = nb_tiles_x_init.value * TILE_SIZE
        let nb_tiles_x_dec = fix_decimal(map_width / tile_size.value)
        return Math.ceil(nb_tiles_x_dec) + 1
    })
    const nb_tiles_y = computed(() => {
        let map_height = nb_tiles_y_init.value * TILE_SIZE
        let nb_tiles_y_dec = fix_decimal(map_height / tile_size.value)
        return Math.ceil(nb_tiles_y_dec) + 1
    })

    const tile_size = computed(() => {
        return get_tile_size_from_zoom(map_store.coords.z)
    })

    const z_coord = computed(() => {
        return Math.ceil(map_store.coords.z)
    })

    onMounted(() => {
        map_store.panning = false
        let x = $cookies.get("coords_x")
        let y = $cookies.get("coords_y")
        let z = $cookies.get("coords_z")
        let offset_x = $cookies.get("offset_display_x")
        let offset_y = $cookies.get("offset_display_y")
        map_store.coords.x = (x == null ? 0 : parseInt(x))
        map_store.coords.y = (y == null ? 0 : parseInt(y))
        map_store.coords.z = (z == null ? 3 : parseFloat(z))
        map_store.offset_display.x = (offset_x == null ? 0 : parseInt(offset_x))
        map_store.offset_display.y = (offset_y == null ? 0 : parseInt(offset_y))
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
                            let grid_ind = (rel_y) * nb_tiles_x.value + rel_x
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
        for (let ind = 0; ind < nb_tiles_x.value * nb_tiles_y.value; ind++) {
            ind_x = ind % nb_tiles_x.value
            ind_y = Math.floor(ind / nb_tiles_x.value)
            grid_coords[ind] = [ map_store.coords.x + ind_x, map_store.coords.y + ind_y ]
        }
        // Load tiles
        grid_coords.forEach((el) => {
            load_tile(el[0], el[1], z_coord.value).catch((error) => { console.log(error) })
        })
    }

    const update_cursor_coords = (e) => {
        map_store.cursor_rel_coords = get_map_coords(map_store.coords, map_store.offset_display, [ e.clientX, e.clientY ], display.value)
        map_store.cursor_rel_coords_rounded.x = Math.floor(map_store.cursor_rel_coords.x * 1000) / 1000
        map_store.cursor_rel_coords_rounded.y = Math.floor(map_store.cursor_rel_coords.y * 1000) / 1000
    }

    const start_panning = (e) => {
        prev_x = e.clientX
        prev_y = e.clientY
        map_store.panning = true
    }

    const stop_panning = () => { map_store.panning = false }

    const pan = (e) => {
        let scroll_x = display.value.scrollLeft + (prev_x - e.clientX)
        let scroll_y = display.value.scrollTop + (prev_y - e.clientY)
        let max_ind = Math.pow(2, Math.ceil(map_store.coords.z))
        let shift_x = 0
        let shift_y = 0
        let i, j
        if (scroll_x < 0 && (map_store.coords.x - 1) >= 0) {
            shift_x = -1
            map_store.coords.x -= 1
            // shift tiles to the right
            for (i = 0; i < nb_tiles_y.value; i++) {
                for (j = nb_tiles_x.value * (i + 1) - 1; j > i * nb_tiles_x.value ; j--) {
                    tile_urls.value[j] = tile_urls.value[j - 1]
                }
            }
        }
        else if (scroll_x > tile_size.value && (map_store.coords.x + nb_tiles_x.value) < max_ind) {
            shift_x = 1
            map_store.coords.x += 1
            // shift tiles to the left
            for (i = 0; i < nb_tiles_y.value; i++) {
                for (j = i * nb_tiles_x.value; j < nb_tiles_x.value * (i + 1) - 1; j++) {
                    tile_urls.value[j] = tile_urls.value[j + 1]
                }
            }
        }
        if (scroll_y < 0 && (map_store.coords.y - 1) >= 0) {
            shift_y = -1
            map_store.coords.y -= 1
            // shift tiles to the bottom
            for (i = 0; i < nb_tiles_x.value; i++) {
                for (j = nb_tiles_y.value - 1; j > 0; j--) {
                    tile_urls.value[j * nb_tiles_x.value + i] = tile_urls.value[(j - 1) * nb_tiles_x.value + i]
                }
            }
        }
        else if (scroll_y > tile_size.value && (map_store.coords.y + nb_tiles_y.value) < max_ind) {
            shift_y = 1
            map_store.coords.y += 1
            // shift tiles to the top
            for (i = 0; i < nb_tiles_x.value; i++) {
                for (j = 0; j < nb_tiles_y.value - 1; j++) {
                    tile_urls.value[j * nb_tiles_x.value + i] = tile_urls.value[(j + 1) * nb_tiles_x.value + i]
                }
            }
        }
        if (shift_x == -1) {
            // load tiles at the left border
            for (i = 0; i < nb_tiles_y.value; i++) {
                load_tile(map_store.coords.x, map_store.coords.y + i, z_coord.value)
            }
            scroll_x += tile_size.value
        }
        else if (shift_x == 1) {
            // load tiles at the right border
            for (i = 0; i < nb_tiles_y.value; i++) {
                load_tile(map_store.coords.x + nb_tiles_x.value - 1, map_store.coords.y + i, z_coord.value)
            }
            scroll_x -= tile_size.value
        }
        if (shift_y == -1) {
            // load tiles at the top border
            for (i = 0; i < nb_tiles_x.value; i++) {
                load_tile(map_store.coords.x + i, map_store.coords.y, z_coord.value)
            }
            scroll_y += tile_size.value
        }
        else if (shift_y == 1) {
            // load tiles at the bottom border
            for (i = 0; i < nb_tiles_x.value; i++) {
                load_tile(map_store.coords.x + i, map_store.coords.y + nb_tiles_y.value - 1, z_coord.value)
            }
            scroll_y -= tile_size.value
        }
        let max_scroll_x = (tile_size.value * nb_tiles_x.value) % (nb_tiles_x_init.value * TILE_SIZE)
        let max_scroll_y = (tile_size.value * nb_tiles_y.value) % (nb_tiles_y_init.value * TILE_SIZE)
        map_store.offset_display.x = Math.min(scroll_x, max_scroll_x)
        display.value.scrollLeft = map_store.offset_display.x
        map_store.offset_display.y = Math.min(scroll_y, max_scroll_y)
        display.value.scrollTop = map_store.offset_display.y
        prev_x = e.clientX
        prev_y = e.clientY
        store_coords_cookie()
    }

    const zoom = (e) => {
        let z = map_store.coords.z
        if (e.deltaY < 0)
            z += 0.5
        else
            z -= 0.5
        z = fix_decimal(z)
        if (z < Z_MIN || z > Z_MAX)
            return
        map_store.coords.z = z
        let vp_coords = get_viewport_coords([ e.clientX, e.clientY ], display.value)
        position_map(map_store.cursor_rel_coords, z, vp_coords)
    }

    const position_map = (pos, zoom, vp_coords) => {
        let nb_tiles_on_axis = Math.pow(2, Math.ceil(zoom))
        let nb_tiles_displayed = get_nb_tiles_displayed(display.value, zoom)
        let current_tile_size = get_tile_size_from_zoom(zoom)
        // X
        let pos_x = pos.x * nb_tiles_on_axis
        let pos_left = pos_x - (vp_coords.x * nb_tiles_displayed.x)
        let e_pos_left = Math.floor(pos_left)
        let dec_pos_left = pos_left - e_pos_left
        map_store.coords.x = e_pos_left
        map_store.offset_display.x = dec_pos_left * current_tile_size
        display.value.scrollLeft = map_store.offset_display.x
        // Y
        let pos_y = pos.y * nb_tiles_on_axis
        let pos_top = pos_y - (vp_coords.y * nb_tiles_displayed.y)
        let e_pos_top = Math.floor(pos_top)
        let dec_pos_top = pos_top - e_pos_top
        map_store.coords.y = e_pos_top
        map_store.offset_display.y = dec_pos_top * current_tile_size
        display.value.scrollTop = map_store.offset_display.y
        store_coords_cookie()
        load_map()
    }

    defineExpose({
        update_cursor_coords, pan, start_panning, stop_panning, zoom, position_map
    })
</script>