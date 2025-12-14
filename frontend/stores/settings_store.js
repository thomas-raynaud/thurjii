import { reactive } from 'vue'
import { PLOT_COLOR_TYPES } from '../lib/enums'

export const settings_store = reactive({
    current_season: null,
    plot_color_type: PLOT_COLOR_TYPES.VARIETY
})