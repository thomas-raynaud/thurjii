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
    lines: [[]],
    lines_done: [[]],
    lines_highlighted: [[]],
    show_plot_names: true,
    // Plot section related arrays, all with the same index
    regions: [ [] ],
    region_centers: [],
    plot_section_names: [],
    regions_color: [],

    map_plot_section_plot: [],
    plot_inds: [],
    plot_names: [],
    plot_centers: [],

    current_region_ind: -1,
    current_line_ind: -1,
    current_line_point_ind: -1,

    line_point_dragged: false,
    line_point_placed: false,

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
    selecting_zone: false,

    line_theta: 0,
    line_step: 10,
    line_spread_min: 2,
    line_spread_max: 100,
})