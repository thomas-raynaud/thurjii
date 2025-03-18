<template>
    <div class="body row justify-content-center">
        <div class="col-auto">
            <p class="fs-3 text-center" v-show="map_store.state == STATE.SELECT_REGION">Sélectionner une région</p>
            <p class="fs-3 text-center" v-show="map_store.state == STATE.PLACE_LINES">Placer les rangs</p>
            <map-container nb-tiles-x="3" nb-tiles-y="2" />
        </div>
        <div class="col">
            <div class="mb-3">
                <input class="form-control" v-model="plot_data.name" placeholder="Nom de la parcelle">
            </div>
            <select-or-create-form
                :form-data="plot_data.cepage"
                :form-list="cepages"
                form-check-label="Ajouter un nouveau cépage"
                form-new-data-placeholder="Nom du cépage"
            />
            <select-or-create-form
                :form-data="plot_data.taille"
                :form-list="tailles"
                form-check-label="Ajouter un nouveau type de taille"
                form-new-data-placeholder="Nom du type de taille"
            />
            <select-or-create-form
                :form-data="plot_data.pliage"
                :form-list="pliages"
                form-check-label="Ajouter un nouveau type de pliage"
                form-new-data-placeholder="Nom du type de pliage"
            />
            <div>
                <p v-show="map_store.state == STATE.PLACE_LINES">{{ "Nombre de rangs : " + map_store.lines.length }}</p>
                <p v-show="map_store.state == STATE.PLACE_LINES">{{ "Superficie : " + area_region + " ha"}}</p>
            </div>
            <div class="invalid-feedback mb-3" :style="{'display': invalid_data ? 'block' : 'none'}">
                Veuillez compléter tous les champs.
            </div>
            <button
                class="btn btn-primary"
                :disabled="map_store.state == STATE.SELECT_REGION"
                @click="create_plot()"
            >
                Créer la parcelle
            </button>
        </div>
    </div>
</template>

<script setup>
    import { computed, ref, onMounted } from 'vue'

    import MapContainer from '../components/map_container.vue'
    import SelectOrCreateForm from '../components/select_or_create_form.vue'
    import { map_store } from '../stores/map_store'
    import { get_area } from '../lib/geometry'
    import { STATE } from '../lib/enums'
    import { send_http_request } from '../lib/request'

    const plot_data = ref({
        name: "",
        cepage: { id: -1, nom: "" },
        taille: { id: -1, nom: "" },
        pliage: { id: -1, nom: "" }
    })
    const cepages = ref([])
    const tailles = ref([])
    const pliages = ref([])
    const invalid_data = ref(false)

    onMounted(() => {
        map_store.state = STATE.SELECT_REGION
        map_store.region = []
        map_store.lines = []
        // Load cepages
        send_http_request("GET", "cepages").then((response) => {
            cepages.value = JSON.parse(response.response)
        })
        // Load tailles
        send_http_request("GET", "tailles").then((response) => {
            tailles.value = JSON.parse(response.response)
        })
        // Load pliages
        send_http_request("GET", "pliages").then((response) => {
            pliages.value = JSON.parse(response.response)
        })
    })

    const area_region = computed(() => {
        let area = get_area(map_store.region)
        let area_h = area / 10000
        return Math.floor(area_h * 100) / 100
    })

    const create_plot = () => {
        invalid_data.value = plot_data.value.nom == ""
            || plot_data.value.cepage.nom == ""
            || plot_data.value.taille.nom == ""
            || plot_data.value.pliage.nom == ""
        if (invalid_data.value)
            return
        console.log(plot_data.value)
        /*send_http_request("POST", "parcelles").then((response) => {
            $router.push('parcelle/' + parcelle.id)
        }).catch((error) => {
            console.error("Could not create plot ...")
            console.error(error)
        })*/
    }
</script>