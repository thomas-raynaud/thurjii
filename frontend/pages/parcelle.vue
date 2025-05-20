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
                                        @click="start_update()"
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
                    <h5>Tâches {{ (no_tasks_registered ? "(aucune)" : "") }}</h5>
                    <ul class="list-group mb-3">
                        <div v-for="tache in parcelle.taches">
                            <li class="list-group-item d-flex justify-content-between align-items-center" v-if="tache.checked">
                                {{ tache.nom }}
                                <span class="badge text-bg-primary rounded-pill">0%</span>
                            </li>
                        </div>
                    </ul>
                    <p>Superficie : {{ parcelle.area }} ha</p>
                </div>
                <div v-show="update_display == true">
                    <parcelle-form :form-data="parcelle" :invalid-data="invalid_data" />
                    <div class="invalid-feedback mb-3" :style="{'display': no_changes_detected ? 'block' : 'none'}">
                        Aucune modification n'a été faite.
                    </div>
                    <div class="row row-cols-auto">
                        <div class="col">
                            <button
                                class="btn btn-primary"
                                @click="update_plot()"
                            >
                                Modifier
                            </button>
                        </div>
                        <div class="col">
                            <button
                                type="button" class="btn btn-light"
                                @click="quit_update()"
                            >
                                Annuler
                            </button>
                        </div>
                    </div>
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
    import { data_store } from '../stores/data_store'
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
        taches: [],
        area: 0
    })
    let parcelle_backup = {}
    const plot_found = ref(false)
    const plot_loading = ref(true)
    const nb_tiles_x = ref(4)
    const nb_tiles_y = ref(3)
    const update_display = ref(false)
    const invalid_data = ref(false)
    const no_tasks_registered = ref(true)
    const no_changes_detected = ref(false)

    onMounted(() => {
        map_store.state = STATE.DISPLAY_PLOT
        map_store.regions = [ [] ]
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
                parcelle.value.area = Math.floor((parcelle_api.properties.area / 10000) * 100) / 100
                let region_api = parcelle_api.geometry.coordinates[0]
                map_store.regions[0] = region_api.map((x) => { return { x: x[0], y: x[1] }})
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
                map_container.value.center_map_on_region(map_store.regions[0])
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
            send_api("GET", "taches").then((response) => {
                parcelle.value.taches = JSON.parse(response.response)
                for (let i = 0; i < parcelle.value.taches.length; i++) {
                    parcelle.value.taches[i].checked = false
                    parcelle.value.taches[i].checked_db = false
                }
                send_api("GET", "taches_par_parcelle/" + parcelle.value.id + "/" + data_store.season).then((response) => {
                    if (response.status != 404) {
                        let taches_parcelle = JSON.parse(response.response)
                        for (let tache_parcelle of taches_parcelle) {
                            // Trouver la tâche correspondante dans parcelle.value.taches
                            for (let i = 0; i < parcelle.value.taches.length; i++) {
                                if (parcelle.value.taches[i].id == tache_parcelle.type_tache) {
                                    parcelle.value.taches[i].checked = true
                                    parcelle.value.taches[i].checked_db = true
                                    no_tasks_registered.value = false
                                    break
                                }
                            }
                        }
                    }
                })
            })
        })
    })

    const update_plot = () => {
        let tache_ids = []
        let are_db_tasks_different = false
        for (let tache of parcelle.value.taches) {
            if (tache.checked) {
                tache_ids.push(tache.id)
            }
            if (tache.checked != tache.checked_db) {
                are_db_tasks_different = true
            }
        }
        let has_plot_changed = has_plot_been_modified()
        if (!has_plot_changed && !are_db_tasks_different) {
            no_changes_detected.value = true
            return
        }
        no_changes_detected.value = false
        let request_promises = []
        if (are_db_tasks_different) {
            request_promises.push(send_api("POST", "taches_par_parcelle/" + parcelle.value.id + "/" + data_store.season, tache_ids))
        }
        if (has_plot_changed) {
            let parcelle_data = {
                id: parcelle.value.id,
                type: "Feature",
                geometry: {
                    type: "Polygon",
                    coordinates: [
                    map_store.regions[0].map((x) => [ x.x, x.y ])
                    ]
                },
                properties: {
                    nom: parcelle.value.nom,
                    cepage: parcelle.value.cepage.id,
                    taille: parcelle.value.taille.id,
                    pliage: parcelle.value.pliage.id
                }
            }
            request_promises.push(send_api("PUT", "parcelles/" + parcelle.value.id, parcelle_data))
        }
        Promise.all(request_promises).then(() => {
            for (let i = 0; i < parcelle.value.taches.length; i++) {
                parcelle.value.taches[i].checked_db = parcelle.value.taches[i].checked
            }
            update_display.value = false
        })
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

    const start_update = () => {
        update_display.value = true
        parcelle_backup = clone_parcelle(parcelle.value)
    }

    const quit_update = () => {
        update_display.value = false
        parcelle.value = clone_parcelle(parcelle_backup)
    }

    const clone_parcelle = (in_parcelle) => {
        let out_parcelle = Object.assign({}, in_parcelle)
        out_parcelle.cepage = Object.assign({}, in_parcelle.cepage)
        out_parcelle.taille = Object.assign({}, in_parcelle.taille)
        out_parcelle.pliage = Object.assign({}, in_parcelle.pliage)
        out_parcelle.taches = []
        for (let tache of in_parcelle.taches) {
            out_parcelle.taches.push(Object.assign({}, tache))
        }
        return out_parcelle
    }

    const has_plot_been_modified = () => {
        return !(parcelle.value.nom == parcelle_backup.nom &&
            parcelle.value.cepage.id == parcelle_backup.cepage.id &&
            parcelle.value.taille.id == parcelle_backup.taille.id &&
            parcelle.value.pliage.id == parcelle_backup.pliage.id
        )
    }
</script>