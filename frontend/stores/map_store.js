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
    lines_done: [],
    lines_highlighted: [],
    show_plot_names: true,
    // Plot related arrays, all with the same index
    regions: [ [] ],
    region_centers: [],
    plot_names: [],

    zone_selection: {
        start: {
            x: 0,
            y: 0
        },
        end: {
            x: 0,
            y: 0
        }
    },
    selecting_zone: false
})