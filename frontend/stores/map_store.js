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
    state: STATE.DISPLAY_VINEYARD,
    line_cursor_coords: {
        x: 0,
        y: 0
    },
    lines: [],
    lines_highlighted: [],
    line_panning: false,
    line_rotating: false,
    line_spreading: false,
    show_plot_names: true,
    // Plot related arrays, all with the same index
    regions: [ [] ],
    region_centers: [],
    plot_names: [],
})