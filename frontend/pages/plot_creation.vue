<template>
    <div class="body row">
        <div class="col">
            <map-container nb-tiles-x="3" nb-tiles-y="2" />
        </div>
        <div class="col">
            <p>{{ map_store.state == 0 ? "Select a region" : "Place the lines" }}</p>
            <p>{{ "x= " + map_store.cursor_rel_coords_rounded.x + " y= " + map_store.cursor_rel_coords_rounded.y + " z= " + map_store.coords.z }}</p>
            <p>{{ "mx= " + merc_coords.x }}</p>
            <p>{{ "my= " + merc_coords.y }}</p>
            <p v-show="map_store.state == 1">{{ "Number of lines: " + map_store.lines.length }}</p>
            <p v-show="map_store.state == 1">{{ "Region area: " + area_region + " ha"}}</p>
        </div>
    </div>
</template>

<script setup>
    import { computed, onMounted, onUnmounted } from 'vue'

    import MapContainer from '../components/map_container.vue'
    import { map_store } from '../stores/map_store'
    import { from_rel_coords_to_mercator } from '../lib/map_navigation'
    import { get_area } from '../lib/geometry'

    onMounted(() => {
        map_store.state = 0
        map_store.region = []
        map_store.lines = []
    })

    onUnmounted(() => {
        console.log("end")
        map_store.state = 0
        map_store.region = []
        map_store.lines = []
    })

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