<template>
    <div class="body">
        <div v-show="plot_found" class="row">
            <div class="col" v-show="plot_found">
                <map-container
                    ref="map_container"
                    :nb-tiles-x="nb_tiles_x" :nb-tiles-y="nb_tiles_y"
                />
            </div>
            <div class="col">
                <h3>{{ parcelle.nom }}</h3>
                <p>Cépage : {{ parcelle.nom_cepage }}</p>
                <p>Taille : {{ parcelle.nom_taille }}</p>
                <p>Pliage : {{ parcelle.nom_pliage }}</p>
                <button
                    type="button" class="btn btn-danger"
                    @click="delete_plot(parcelle.id)"
                >
                    Supprimer
                </button>
            </div>
        </div>
        <p v-show="!plot_found && !plot_loading">Parcelle #{{ route.params.id }} inexistante</p>
    </div>
</template>

<script setup>
    import { ref, useTemplateRef, onMounted, nextTick } from 'vue'
    import { useRoute, useRouter } from 'vue-router'

    import MapContainer from '../components/map_container.vue'
    import { map_store } from '../stores/map_store'
    import { send_api } from '../lib/request'
    import { STATE } from '../lib/enums'

    const router = useRouter()

    const map_container = useTemplateRef("map_container")
    const route = useRoute()
    const parcelle = ref({})
    const plot_found = ref(false)
    const plot_loading = ref(true)
    const nb_tiles_x = ref(3)
    const nb_tiles_y = ref(2)

    onMounted(() => {
        map_store.state = STATE.DISPLAY_PLOT
        map_store.region = []
        map_store.lines = []
        let get_promises = []
        get_promises.push(new Promise((resolve) => {
            send_api("GET", "parcelles/" + route.params.id).then((response) => {
                let parcelle_api = JSON.parse(response.response)
                parcelle.value = parcelle_api.properties
                parcelle.value.id = parcelle_api.id
                let region_api = parcelle_api.geometry.coordinates[0]
                map_store.region = region_api.map((x) => { return { x: x[0], y: x[1] }})
                plot_loading.value = false
                plot_found.value = true
                resolve()
            }).catch((error) => {
                console.error("Error when loading plot #" + route.params.id + " ...")
                console.error(error)
            })
        }))
        get_promises.push(new Promise((resolve) => {
            send_api("GET", "parcelles/" + route.params.id + "/rangs").then((response) => {
                let rangs_api = JSON.parse(response.response).features
                for (let i = 0; i < rangs_api.length; i++) {
                    map_store.lines.push({
                        start: {
                            x: rangs_api[i].geometry.coordinates[0][0],
                            y: rangs_api[i].geometry.coordinates[0][1],
                        },
                        end: {
                            x: rangs_api[i].geometry.coordinates[1][0],
                            y: rangs_api[i].geometry.coordinates[1][1],
                        }
                    })
                }
                resolve()
            }).catch((error) => {
                console.error("Error when loading lines of plot #" + route.params.id + " ...")
                console.error(error)
            })
        }))
        Promise.all(get_promises).then(() => {
            map_store.state = STATE.DISPLAY_PLOT
            nextTick(() => {
                map_container.value.center_map_on_region()
            })
            send_api("GET", "cepages/" + parcelle.value.cepage).then((response) => {
                parcelle.value.nom_cepage = JSON.parse(response.response).nom
            })
            send_api("GET", "tailles/" + parcelle.value.taille).then((response) => {
                parcelle.value.nom_taille = JSON.parse(response.response).nom
            })
            send_api("GET", "pliages/" + parcelle.value.pliage).then((response) => {
                parcelle.value.nom_pliage = JSON.parse(response.response).nom
            })
        })
    })

    const delete_plot = (plot_id) => {
        send_api("DELETE", "parcelles/" + plot_id).then((response) => {
            if (response.status == 500) {
                console.error("Could not delete plot #" + plot_id + " ...")
            }
            else {
                router.push('/')
            }
        }).catch((error) => {
            console.error("Could not delete plot #" + plot_id + " ...")
            console.error(error)
        })
    }
</script>