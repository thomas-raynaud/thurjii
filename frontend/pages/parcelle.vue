<template>
    <div class="body">
        <div v-show="plot_found" class="row container-fluid">
            <div class="col" v-show="plot_found">
                <map-container
                    ref="map_container"
                    :nb-tiles-x="nb_tiles_x" :nb-tiles-y="nb_tiles_y"
                />
            </div>
            <div class="col">
                <div v-show="update_display == false">
                    <div class="row align-items-center mb-3">
                        <div class="col-8">
                            <h3>{{ parcelle.nom }}</h3>
                        </div>
                        <div class="col">
                            <div class="row row-cols-auto">
                                <div class="col">
                                    <button
                                        type="button" class="btn btn-outline-primary"
                                        @click="update_display = true"
                                    >
                                        Modifier
                                    </button>
                                </div>
                                <div class="col">
                                    <button
                                        type="button" class="btn btn-outline-danger"
                                        @click="delete_plot()"
                                    >
                                        Supprimer
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <p>Cépage : {{ parcelle.cepage.nom }}</p>
                    <p>Taille : {{ parcelle.taille.nom }}</p>
                    <p>Pliage : {{ parcelle.pliage.nom }}</p>
                    <h5>Tâches {{ (parcelle.taches.length == 0 ? "(aucune)" : "") }}</h5>
                    <ul class="list-group mb-3">
                        <li class="list-group-item d-flex justify-content-between align-items-center" v-for="tache in parcelle.taches">
                            {{ tache.nom }}
                            <span class="badge text-bg-primary rounded-pill">0%</span>
                        </li>
                    </ul>
                </div>
                <div v-show="update_display == true">
                    <parcelle-form :form-data="parcelle" :invalid-data="invalid_data" />
                    <button
                        class="btn btn-primary"
                        @click="update_plot()"
                    >
                        Modifier
                    </button>
                </div>
            </div>
        </div>
        <p v-show="!plot_found && !plot_loading">Parcelle #{{ route.params.id }} inexistante</p>
    </div>
</template>

<script setup>
    import { ref, useTemplateRef, onMounted, nextTick } from 'vue'
    import { useRoute, useRouter } from 'vue-router'

    import MapContainer from '../components/map_container.vue'
    import ParcelleForm from '../components/parcelle_form.vue'
    import { map_store } from '../stores/map_store'
    import { send_api } from '../lib/request'
    import { STATE } from '../lib/enums'

    const router = useRouter()

    const map_container = useTemplateRef("map_container")
    const route = useRoute()
    const parcelle = ref({
        id: -1,
        nom: "",
        cepage: { id: -1, nom: " "},
        taille: { id: -1, nom: " "},
        pliage: { id: -1, nom: " "},
        taches: []
    })
    const plot_found = ref(false)
    const plot_loading = ref(true)
    const nb_tiles_x = ref(4)
    const nb_tiles_y = ref(3)
    const update_display = ref(false)
    const invalid_data = ref(false)

    onMounted(() => {
        map_store.state = STATE.DISPLAY_PLOT
        map_store.region = []
        map_store.lines = []
        let get_promises = []
        get_promises.push(new Promise((resolve) => {
            send_api("GET", "parcelles/" + route.params.id).then((response) => {
                let parcelle_api = JSON.parse(response.response)
                parcelle.value.id = parcelle_api.id
                parcelle.value.nom = parcelle_api.properties.nom
                parcelle.value.cepage.id = parcelle_api.properties.cepage
                parcelle.value.taille.id = parcelle_api.properties.taille
                parcelle.value.pliage.id = parcelle_api.properties.pliage
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
            send_api("GET", "cepages/" + parcelle.value.cepage.id).then((response) => {
                parcelle.value.cepage.nom = JSON.parse(response.response).nom
            })
            send_api("GET", "tailles/" + parcelle.value.taille.id).then((response) => {
                parcelle.value.taille.nom = JSON.parse(response.response).nom
            })
            send_api("GET", "pliages/" + parcelle.value.pliage.id).then((response) => {
                parcelle.value.pliage.nom = JSON.parse(response.response).nom
            })
            send_api("GET", "taches_par_parcelles/" + parcelle.value.id).then((response) => {
                if (response.status == 404) {
                    parcelle.value.taches = []
                }
                else
                    parcelle.value.taches = JSON.parse(response.response)
            })
        })
    })

    const update_plot = () => {
        
    }

    const delete_plot = () => {
        send_api("DELETE", "parcelles/" + parcelle.value.id).then((response) => {
            if (response.status == 500) {
                console.error("Could not delete plot #" + parcelle.value.id + " ...")
            }
            else {
                router.push('/')
            }
        }).catch((error) => {
            console.error("Could not delete plot #" + parcelle.value.id + " ...")
            console.error(error)
        })
    }
</script>