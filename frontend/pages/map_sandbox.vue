<template>
    <map-container ref="map_container" nb-tiles-x="7" nb-tiles-y="3" />
</template>

<script setup>
    import { computed, onMounted, useTemplateRef } from 'vue'

    import MapContainer from '../components/map_container.vue'
    import { map_store } from '../stores/map_store'
    import { data_store } from '../stores/data_store'
    import { from_rel_coords_to_mercator } from '../lib/map_navigation'
    import { get_area } from '../lib/geometry'
    import { STATE } from '../lib/enums'

    const map_container = useTemplateRef("map_container")

    onMounted(() => {
        map_store.state = STATE.DISPLAY_VINEYARD
        map_store.regions = [ [] ]

        data_store.compute_parcelles_bb().then(() => {
            map_container.value.center_map_on_region([ data_store.parcelles_bb.min, data_store.parcelles_bb.max ])
            map_store.regions = data_store.parcelles_regions
        })
    })

    const merc_coords = computed(() => {
        let m_coords = from_rel_coords_to_mercator(map_store.cursor_rel_coords.x, map_store.cursor_rel_coords.y)
        return {
            x: Math.floor(m_coords.x * 100) / 100,
            y: Math.floor(m_coords.y * 100) / 100
        }
    })

    const area_region = computed(() => {
        let area = get_area(map_store.regions.at(-1))
        let area_h = area / 10000
        return Math.floor(area_h * 100) / 100
    })
</script>