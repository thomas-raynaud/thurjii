<template>
    <div class="row row-cols-auto">
        <div class="col">
            <button
                type="button"
                :class="[
                    'btn',
                    map_store.state == STATE.ADD_PLOT_SECTION ? 'btn-primary' : 'btn-secondary'
                ]"
                @click="add_plot_section()"
            >
                Contours de la section
            </button>
        </div>
        <div class="col">
            <button
                type="button"
                :class="[
                    'btn',
                    map_store.state == STATE.EDIT_LINES_GLOBAL_PLACEMENT ? 'btn-primary' : 'btn-secondary'
                ]"
                :disabled="!section_drawn"
                @click="edit_lines_global_placement()"
            >
                Placement des rangs
            </button>
        </div>
        <div class="col">
            <button
                type="button"
                :class="[
                    'btn',
                    map_store.state == STATE.EDIT_LINES ? 'btn-primary' : 'btn-secondary'
                ]"
                :disabled="!section_drawn"
                @click="edit_lines()"
            >
                Modifier les rangs
            </button>
        </div>
    </div>
</template>

<script setup>
    import { onMounted, computed } from 'vue'

    import { map_store } from '../stores/map_store'
    import { STATE } from '../lib/enums'

    const section_drawn = computed(() => {
        if (map_store.current_region_ind == -1) return false
        if (map_store.regions[map_store.current_region_ind].length <= 2) return false
        if (map_store.lines[map_store.current_region_ind] == 0) return false
        return true
    })

    onMounted(() => {
    })

    const add_plot_section = () => {
        map_store.regions[map_store.current_region_ind] = []
        map_store.lines[map_store.current_region_ind] = []
        map_store.state = STATE.ADD_PLOT_SECTION
    }

    const edit_lines_global_placement = () => {
        map_store.state = STATE.EDIT_LINES_GLOBAL_PLACEMENT
    }

    const edit_lines = () => {
        map_store.state = STATE.EDIT_LINES
    }
</script>