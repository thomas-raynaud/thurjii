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
    panning: false,
    state: 0, // 0 = select region, 1 = place lines,
    line_cursor_coords: {
        x: 0,
        y: 0
    }
})