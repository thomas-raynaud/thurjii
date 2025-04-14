<template>
    <div class="row">
        <div class="col">
            <map-container ref="map_container" nb-tiles-x="5" nb-tiles-y="3" />
        </div>
        <div class="col">
            <input class="form-check-input me-1" type="checkbox" v-model="map_store.show_plot_names">
            <label class="form-check-label">Afficher le nom des parcelles</label>
        </div>
    </div>
</template>

<script setup>
    import { onMounted, useTemplateRef, watch } from 'vue'

    import MapContainer from '../components/map_container.vue'
    import { map_store } from '../stores/map_store'
    import { data_store } from '../stores/data_store'
    import { STATE } from '../lib/enums'

    const map_container = useTemplateRef("map_container")

    onMounted(() => {
        map_store.state = STATE.DISPLAY_VINEYARD
        map_store.regions = [ [] ]
        map_store.show_plot_names = true

        data_store.compute_parcelles_bb().then(() => {
            map_container.value.center_map_on_region([ data_store.parcelles_bb.min, data_store.parcelles_bb.max ])
            map_store.regions = data_store.parcelles_regions
        })
    })

    watch(() => map_store.show_plot_names, () => {
        map_container.value.redraw()
    })
</script>