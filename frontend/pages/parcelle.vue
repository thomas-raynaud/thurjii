<template>
    <div class="body row">
        <div class="col">
            <map-container nb-tiles-x="3" nb-tiles-y="2" />
        </div>
        <div class="col">
        </div>
    </div>
</template>

<script setup>
    import { ref, computed, onMounted, onUnmounted } from 'vue'
    import { useRoute } from 'vue-router'

    import MapContainer from '../components/map_container.vue'
    import { map_store } from '../stores/map_store'
    import { from_rel_coords_to_mercator } from '../lib/map_navigation'
    import { get_area } from '../lib/geometry'
    import { send_http_request } from '../lib/request'
    import { STATE } from '../lib/enums'

    const route = useRoute()
    const parcelle = ref()

    onMounted(() => {
        map_store.state = STATE.DISPLAY_PLOT
        map_store.region = []
        map_store.lines = []
        send_http_request("GET", "parcelles/" + route.params.id).then((response) => {
            if (response.status == 0) {
                console.log("Error when loading parcelles ...")
            }
            else {
                parcelle.value = JSON.parse(response.response)
                console.log(parcelle.value.region)
            }
            
        }).catch((error) => {
            console.log("Error when loading parcelles ...")
            console.log(error)
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
        let area = get_area(map_store.region)
        let area_h = area / 10000
        return Math.floor(area_h * 100) / 100
    })
</script>