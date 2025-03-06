<template>
    <div class="body row">
        <map-container nb-tiles-x="3" nb-tiles-y="2" />
    </div>
</template>

<script setup>
    import { computed } from 'vue'

    import MapContainer from '../components/map_container.vue'
    import { map_store } from '../stores/map_store'
    import { from_rel_coords_to_mercator } from '../lib/map_navigation'
    import { get_area } from '../lib/geometry'

    const merc_coords = computed(() => {
        let m_coords = from_rel_coords_to_mercator(map_store.cursor_rel_coords.x, map_store.cursor_rel_coords.y)
        return {
            x: Math.floor(m_coords.x * 100) / 100,
            y: Math.floor(m_coords.y * 100) / 100
        }
    })

    const area_region = computed(() => {
        let area = get_area(map_store.region)
        let area_h = area / 10000
        return Math.floor(area_h * 100) / 100
    })
</script>