import { reactive } from 'vue'

import { STATE } from '../lib/enums'

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
    offset_display: {
        x: 0,
        y: 0
    },
    state: STATE.SELECT_REGION,
    line_cursor_coords: {
        x: 0,
        y: 0
    },
    region: [],
    lines: [],
    line_panning: false,
    line_rotating: false,
    line_spreading: false
})