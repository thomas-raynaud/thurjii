<template>
    <div class="body row">
        <div class="col" v-show="parcelle_found">
            <map-container
                ref="map_container"
                :nb-tiles-x="nb_tiles_x" :nb-tiles-y="nb_tiles_y"
            />
        </div>
        <p v-show="!parcelle_found">Parcelle #{{ route.params.id }} inexistante</p>
        <div class="col">
        </div>
    </div>
</template>

<script setup>
    import { ref, useTemplateRef, onMounted } from 'vue'
    import { useRoute } from 'vue-router'

    import MapContainer from '../components/map_container.vue'
    import { map_store } from '../stores/map_store'
    import { send_http_request } from '../lib/request'
    import { STATE } from '../lib/enums'

    const map_container = useTemplateRef("map_container")
    const route = useRoute()
    const parcelle = ref()
    const parcelle_found = ref()
    const nb_tiles_x = ref(3)
    const nb_tiles_y = ref(2)

    onMounted(() => {
        map_store.state = STATE.DISPLAY_PLOT
        map_store.region = []
        map_store.lines = []
        send_http_request("GET", "parcelles/" + route.params.id).then((response) => {
            if (response.status == 0) {
                console.error("Error when loading plot #" + route.params.id + " ...")
            }
            else {
                parcelle.value = JSON.parse(response.response)
                map_store.region = parcelle.value.region
                parcelle_found.value = true
                map_store.state = STATE.DISPLAY_PLOT
                map_container.value.center_map_on_region()
            }
            
        }).catch((error) => {
            console.error("Error when loading plot #" + route.params.id + " ...")
            console.error(error)
        })
    })
</script>