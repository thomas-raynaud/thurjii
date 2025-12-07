<template>
    <div>
        <div class="row row-cols-auto mb-3">
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
                    @click="map_store.state = STATE.EDIT_LINES_GLOBAL_PLACEMENT"
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
                    @click="map_store.state = STATE.EDIT_LINES"
                >
                    Modifier les rangs
                </button>
            </div>
            <div class="col">
                <button
                    type="button"
                    :class="[
                        'btn',
                        map_store.state == STATE.ADD_LINE ? 'btn-primary' : 'btn-secondary'
                    ]"
                    :disabled="!section_drawn"
                    @click="map_store.state = STATE.ADD_LINE"
                >
                    Ajouter des rangs
                </button>
            </div>
            <div class="col">
                <button
                    type="button"
                    :class="[
                        'btn',
                        map_store.state == STATE.REMOVE_LINE ? 'btn-primary' : 'btn-secondary'
                    ]"
                    :disabled="!section_drawn"
                    @click="map_store.state = STATE.REMOVE_LINE"
                >
                    Supprimer des rangs
                </button>
            </div>
        </div>
        <div v-show="map_store.state == STATE.EDIT_LINES_GLOBAL_PLACEMENT">
            <div class="row">
                <div class="col-4">
                    <label class="form-label">Ecart entre rangs</label>
                </div>
                <div class="col-8">
                    <input type="range" class="form-range" v-model="map_store.line_step" :min="map_store.line_spread_min" :max="map_store.line_spread_max" step="0.2">
                </div>
            </div>
            <div class="row">
                <div class="col-4">
                    <label class="form-label">Orientation des rangs</label>
                </div>
                <div class="col-8">
                    <input type="range" class="form-range" v-model="map_store.line_theta" min="0" max="360" step="0.5">
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
    .row > .col {
        margin-bottom: 0.5rem;
    }
</style>

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
</script>