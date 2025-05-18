<template>
    <div class="body row justify-content-center">
        <div class="col-auto">
            <map-container ref="map_container" nb-tiles-x="3" nb-tiles-y="2" />
        </div>
        <div class="col">
            <button
                class="btn btn-primary"
                @click="create_log()"
            >
                Créer le log
            </button>
        </div>
    </div>
</template>

<script setup>
    import { ref, onMounted, useTemplateRef } from 'vue'

    import MapContainer from '../components/map_container.vue'
    import { send_api } from '../lib/request'


    const plot_data = ref({
        nom: "",
        cepage: { id: -1, nom: "" },
        taille: { id: -1, nom: "" },
        pliage: { id: -1, nom: "" },
        taches: []
    })
    const invalid_data = ref(false)
    const map_container = useTemplateRef("map_container")

    onMounted(() => {
    })

    const create_log = () => {
    }
</script>