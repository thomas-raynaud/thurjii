<template>
    <div class="body row">
        <map-container nb-tiles-x="3" nb-tiles-y="2" />
        <p>{{ "x= " + map_store.cursor_coords.x + " y= " + map_store.cursor_coords.y + " z= " + map_store.coords.z }}</p>
        <p>{{ "mx= " + merc_cords.x}}</p>
        <p>{{ "my= " + merc_cords.y}}</p>
    </div>
</template>

<script setup>
    import { computed } from 'vue'

    import MapContainer from '../components/map_container.vue'
    import { map_store } from '../stores/map_store'
    import { from_tile_coord_to_mercator } from '../lib/map_navigation'

    const merc_cords = computed(() => {
        let m_coords = from_tile_coord_to_mercator(map_store.cursor_coords.x, map_store.cursor_coords.y, map_store.coords.z)
        return {
            x: Math.floor(m_coords.x * 100) / 100,
            y: Math.floor(m_coords.y * 100) / 100
        }
    })
</script>