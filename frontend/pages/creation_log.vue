<template>
    <div class="body row justify-content-center">
        <div class="row mb-3">
            <select class="form-select" v-model="parcelle_id">
                <option value="-1">Sélectionnez une parcelle</option>
                <option v-for="parcelle in parcelles" :value="parcelle.id"> {{ parcelle.nom }} </option>
            </select>
        </div>
        <div class="col-auto">
            <map-container ref="map_container" nb-tiles-x="3" nb-tiles-y="2" />
        </div>
        <div class="col">
            <select class="form-select mb-3" v-model="task_id" :disabled="parcelle_id==-1">
                <option value="-1">Sélectionnez une tâche</option>
                <option v-for="task in tasks_parcelle" :value="task.id"> {{ task.nom }} </option>
            </select>
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
    import { ref, onMounted, useTemplateRef, watch, toRaw } from 'vue'

    import MapContainer from '../components/map_container.vue'
    import { send_api } from '../lib/request'
    import { data_store } from '../stores/data_store'
    import { map_store } from '../stores/map_store'
    import { STATE } from '../lib/enums'

    const parcelle_id = ref(-1)
    const parcelles = ref([])
    const task_id = ref(-1)
    const tasks = ref([])
    const tasks_parcelle = ref([])
    const log_data = ref({
    })
    const invalid_data = ref(false)
    const map_container = useTemplateRef("map_container")

    onMounted(() => {
        send_api("GET", "parcelles").then((response) => {
            if (response.status == 0) {
                console.error("Error when loading plots ...")
            }
            else {
                let parcelles_api = JSON.parse(response.response).features
                parcelles.value = []
                parcelles_api.forEach(parcelle_api => {
                    parcelles.value.push({
                        id: parcelle_api.id,
                        nom: parcelle_api.properties.nom,
                        region: parcelle_api.geometry.coordinates[0].map((x) => { return { x: x[0], y: x[1] }})
                    })
                })
                data_store.compute_parcelles_bb().then(() => {
                    configure_map()
                    load_tasks()
                })
            }
            
        }).catch((error) => {
            console.error("Error when loading plots ...")
            console.error(error)
        })
        send_api("GET", "taches").then((response) => {
            if (response.status == 0) {
                console.error("Error when loading tasks ...")
            }
            else {
                tasks.value = JSON.parse(response.response)
            }
            
        }).catch((error) => {
            console.error("Error when loading tasks ...")
            console.error(error)
        })
    })

    const configure_map = () => {
        if (parcelle_id.value == -1) {
            map_store.state = STATE.DISPLAY_VINEYARD
            map_store.regions = [ [] ]
            map_store.show_plot_names = false
            map_container.value.center_map_on_region([ data_store.parcelles_bb.min, data_store.parcelles_bb.max ])
            map_store.regions = data_store.parcelles_regions
        }
        else {
            map_store.state = STATE.DISPLAY_PLOT
            for (let parcelle of parcelles.value) {
                if (parcelle.id == parcelle_id.value) {
                    map_store.regions = [ toRaw(parcelle.region) ]
                }
            }
            map_container.value.center_map_on_region(map_store.regions[0])
        }
    }

    const load_tasks = () => {
        tasks_parcelle.value = []
        task_id.value = -1
        if (parcelle_id.value != -1) {
            send_api("GET", "taches_par_parcelle/" + parcelle_id.value + "/" + data_store.season).then((response) => {
                if (response.status != 404) {
                    let tasks_parcelle_api = JSON.parse(response.response)
                    for (let task_p of tasks_parcelle_api) {
                        for (let task of tasks.value) {
                            if (task_p.type_tache == task.id) {
                                tasks_parcelle.value.push(task)
                                break
                            }
                        }
                    }
                    if (tasks_parcelle.value.length > 0)
                        task_id.value = tasks_parcelle.value[0].id
                }
            })
        }
    }

    watch(parcelle_id, () => {
        configure_map()
        load_tasks()
    })

    const create_log = () => {
    }
</script>