import { reactive } from 'vue'

export const map_store = reactive({
    coords: {
        x: 0,
        y: 0,
        z: 3
    },
    cursor_coords: {
        x: 0,
        y: 0
    }
})