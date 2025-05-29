<template>
    <div class="body row justify-content-center">
        <div class="row mb-3">
            <select class="form-select" v-model="log_data.plot_id">
                <option value="-1">Sélectionnez une parcelle</option>
                <option v-for="plot in plots" :value="plot.id"> {{ plot.name }} </option>
            </select>
        </div>
        <div class="col-auto">
            <map-container ref="map_container" nb-tiles-x="3" nb-tiles-y="2" />
        </div>
        <div class="col">
            <input type="date" class="mb-3" v-model="log_data.date" :disabled="log_data.plot_id==-1">
            <select class="form-select mb-3" v-model="log_data.plot_task_id" :disabled="log_data.plot_id==-1">
                <option value="-1">Sélectionnez une tâche</option>
                <option v-for="task in plot_tasks" :value="task.id"> {{ task.name }} </option>
            </select>
            <input 
                class="form-control mb-3"
                v-model="log_data.nb_hours"
                placeholder="Nombre d'heures"
                type="number"
                :disabled="log_data.plot_id==-1"
            />
            <textarea
                class="form-control mb-3"
                v-model="log_data.comment"
                placeholder="Commentaire"
                :disabled="log_data.plot_id==-1">
            </textarea>
            <div class="invalid-feedback mb-3" :style="{'display': invalid_data ? 'block' : 'none'}">
                Veuillez compléter tous les champs. Assurez-vous que les champs saisis soient valides.
            </div>
            <button
                class="btn btn-primary"
                @click="create_log()"
                :disabled="log_data.plot_id==-1"
            >
                Créer le log
            </button>
        </div>
    </div>
    <toast ref="toast_component" />
</template>

<script setup>
    import { ref, onMounted, useTemplateRef, watch, toRaw } from 'vue'

    import MapContainer from '../components/map_container.vue'
    import Toast from '../components/toast.vue'
    import { settings_store } from '../stores/settings_store'
    import { map_store } from '../stores/map_store'
    import { send_api } from '../lib/request'
    import {
        retrieve_plot_season_plot_tasks,
        retrieve_plots,
        retrieve_tasks,
        retrieve_plot_lines
    } from '../lib/api_retrieval'
    import { STATE } from '../lib/enums'
    import { compute_vineyard_bb } from '../lib/map_navigation'

    const map_container = useTemplateRef("map_container")
    const toast_component = useTemplateRef("toast_component")
    const invalid_data = ref(false)
    const plots = ref([])
    const tasks = ref([])
    const plot_tasks = ref([])
    const log_data = ref({
        plot_id: -1,
        plot_task_id: -1,
        nb_hours: undefined,
        comment: "",
        date: undefined
    })
    let vineyard_bb = { min: -1, max: -1 }

    onMounted(() => {
        retrieve_plots().then((in_plots) => {
            plots.value = in_plots
            vineyard_bb = compute_vineyard_bb(in_plots)
            configure_map()
            update_map_lines()
        })
        retrieve_tasks().then((in_tasks) => {
            tasks.value = in_tasks
        })
        // Initial date: today
        let today = new Date()
        let dd = String(today.getDate()).padStart(2, '0')
        let mm = String(today.getMonth() + 1).padStart(2, '0')
        let yyyy = today.getFullYear()
        log_data.value.date = yyyy + "-" + mm + "-" + dd
    })

    const configure_map = () => {
        if (log_data.value.plot_id == -1) {
            map_store.state = STATE.DISPLAY_VINEYARD
            map_store.regions = []
            map_store.lines_highlighted = []
            for (let plot of plots.value) {
                map_store.regions.push(toRaw(plot.region))
            }
            map_store.show_plot_names = false
            map_container.value.center_map_on_region([ vineyard_bb.min, vineyard_bb.max ])
        }
        else {
            map_store.state = STATE.DISPLAY_PLOT
            for (let plot of plots.value) {
                if (plot.id == log_data.value.plot_id) {
                    map_store.regions = [ toRaw(plot.region) ]
                    break
                }
            }
            map_container.value.center_map_on_region(map_store.regions[0])
            retrieve_plot_lines(log_data.value.plot_id).then((lines) => {
                map_store.lines = lines
                map_container.value.redraw()
            }).catch(() => {})
        }
    }

    const update_map_lines = () => {
        map_store.lines_highlighted = []
        map_store.lines_done = []
        if (log_data.value.plot_task_id == -1) {
            map_container.value.redraw()
            return
        }
        send_api("GET", "plots/" + log_data.value.plot_id + "/lines/" + settings_store.current_season + "/state").then((response) => {
            let line_states = JSON.parse(response.response)
            for (let line_state of line_states) {
                if (line_state.done) {
                    map_store.lines_done.push({
                        start: { x: line_state.line_location.start[0], y: line_state.line_location.start[1] },
                        end: { x: line_state.line_location.end[0], y: line_state.line_location.end[1] },
                        id: line_state.line
                    })
                }
            }
            map_container.value.redraw()
        })
    }

    const load_plot_tasks = () => {
        return new Promise((resolve, reject) => {
            plot_tasks.value = []
            log_data.value.plot_task_id = -1
            if (log_data.value.plot_id != -1) {
                retrieve_plot_season_plot_tasks(log_data.value.plot_id, settings_store.current_season).then((in_plot_tasks) => {
                    for (let in_plot_task of in_plot_tasks) {
                        plot_tasks.value.push({
                            id: in_plot_task.id,
                            name: in_plot_task.task_name
                        })
                    }
                    resolve()
                })
                .catch((error) => {
                    console.error(error)
                    reject(error)
                })
            }
        })
        
    }

    watch(() => log_data.value.plot_id, () => {
        configure_map()
        load_plot_tasks().then(() => {
            update_map_lines()
        })
        
    })

    watch(() => log_data.value.plot_task_id, () => {
        if (log_data.value.plot_task_id == -1)
            map_store.state = STATE.DISPLAY_PLOT
        else
            map_store.state = STATE.SELECT_LINES
        update_map_lines()
    })

    const create_log = () => {
        // Check if data is valid
        if (log_data.value.plot_task_id == -1 || typeof(log_data.value.nb_hours) !== "number") {
            invalid_data.value = true
            return
        }
        else {
            invalid_data.value = false
            let log_post_data = {
                plot_task: log_data.value.plot_task_id,
                nb_hours: log_data.value.nb_hours,
                comment: log_data.value.comment,
                date: log_data.value.date
            }
            send_api("POST", "logs", log_post_data)
            .then((response) => {
                if (response.status == 400) {
                    console.error(JSON.parse(response.response))
                    toast_component.value.display_toast("Erreur : le log n'a pas pu être créé")
                    return
                }
                toast_component.value.display_toast("Log créé")
                log_data.value.plot_task_id = -1
                log_data.value.nb_hours =  undefined
                log_data.value.comment = ""
            })
            .catch((error) => {
                console.error(error)
                toast_component.value.display_toast("Erreur : le log n'a pas pu être créé")
            })
            
        }
    }
</script>