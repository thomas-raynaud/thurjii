import { reactive } from 'vue'

export const map_store = reactive({
    coords: {
        x: 0,
        y: 0,
        z: 3
    },
    cursor_rel_coords: {
        x: 0,
        y: 0
    },
    cursor_rel_coords_rounded: {
        x: 0,
        y: 0
    },
    offset_display: {
        x: 0,
        y: 0
    },
    panning: false
})