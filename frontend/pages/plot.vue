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
                            <h3>{{ plot.name }}</h3>
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
                    <p>Cépage : {{ plot.variety.name }}</p>
                    <p>Taille : {{ plot.pruning.name }}</p>
                    <p>Pliage : {{ plot.folding.name }}</p>
                    <h5>Tâches {{ (no_tasks_registered ? "(aucune)" : "") }}</h5>
                    <ul class="list-group mb-3">
                        <div v-for="task in plot.tasks">
                            <li :class="[
                                    'list-group-item', 'd-flex', 'justify-content-between', 'align-items-center',
                                    active_task_id == task.plot_task_id ? 'active' : ''
                                ]"
                                v-if="task.checked" @click="select_task(task.plot_task_id)">
                                {{ task.name }}
                                <span class="badge text-bg-primary rounded-pill"> {{ Math.round((task.nb_lines_done / task.line_states.length) * 10000) / 100 }}%</span>
                            </li>
                        </div>
                    </ul>
                    <p>Superficie : {{ plot.area }} ha</p>
                    <p>{{ map_store.lines.length }} rangs</p>
                    <p v-show="map_store.lines_done.length > 0">{{ map_store.lines_done.length }} rangs terminés</p>
                </div>
                <div v-show="update_display == true">
                    <plot-form :form-data="plot" :invalid-data="invalid_data" />
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
    import PlotForm from '../components/plot_form.vue'
    import { settings_store } from '../stores/settings_store'
    import { map_store } from '../stores/map_store'
    import { send_api } from '../lib/request'
    import { STATE } from '../lib/enums'
    import {
        retrieve_plot,
        retrieve_plot_season_plot_tasks,
        retrieve_plot_lines,
        retrieve_plot_line_states,
        retrieve_tasks,
        get_current_season
    } from '../lib/api_retrieval'

    const router = useRouter()

    const map_container = useTemplateRef("map_container")
    const route = useRoute()
    const plot = ref({
        id: -1,
        name: "",
        variety: { id: -1, name: " "},
        pruning: { id: -1, name: " "},
        folding: { id: -1, name: " "},
        tasks: [],
        area: 0
    })
    let plot_backup = {}
    const plot_found = ref(false)
    const plot_loading = ref(true)
    const nb_tiles_x = ref(4)
    const nb_tiles_y = ref(3)
    const update_display = ref(false)
    const invalid_data = ref(false)
    const no_tasks_registered = ref(true)
    const no_changes_detected = ref(false)
    const active_task_id = ref(-1)

    onMounted(() => {
        map_store.state = STATE.DISPLAY_PLOT
        map_store.regions = [ [] ]
        map_store.lines = []
        map_store.lines_done = []
        let get_promises = []
        plot.value.id = route.params.id
        get_promises.push(new Promise((resolve) => {
            retrieve_plot(plot.value.id).then((plot_api) => {
                plot.value.name = plot_api.name
                plot.value.variety.id = plot_api.variety
                plot.value.pruning.id = plot_api.pruning
                plot.value.folding.id = plot_api.folding
                plot.value.area = Math.floor((plot_api.area / 10000) * 100) / 100
                map_store.regions = [ plot_api.region ]
                plot_loading.value = false
                plot_found.value = true
                resolve()
            }).catch((error) => {
                console.error("Error when loading plot #" + plot.value.id + " ...")
                console.error(error)
            })
        }))
        get_promises.push(new Promise((resolve) => {
            retrieve_plot_lines(plot.value.id).then((lines) => {
                map_store.lines = lines
                resolve()
            }).catch(() => {})
        }))
        get_promises.push(new Promise((resolve) => {
            retrieve_tasks().then((tasks) => {
                plot.value.tasks = tasks
                for (let i = 0; i < plot.value.tasks.length; i++) {
                    plot.value.tasks[i].checked = false
                    plot.value.tasks[i].checked_db = false
                }
                resolve()
            })
        }))
        get_promises.push(new Promise((resolve) => {
            get_current_season().then((year) =>  {
                settings_store.current_season = year
                resolve()
            })
        }))
        Promise.all(get_promises).then((results) => {
            map_store.state = STATE.DISPLAY_PLOT
            nextTick(() => {
                map_container.value.center_map_on_region(map_store.regions[0])
            })
            send_api("GET", "varieties/" + plot.value.variety.id).then((response) => {
                plot.value.variety.name = JSON.parse(response.response).name
            })
            send_api("GET", "prunings/" + plot.value.pruning.id).then((response) => {
                plot.value.pruning.name = JSON.parse(response.response).name
            })
            send_api("GET", "foldings/" + plot.value.folding.id).then((response) => {
                plot.value.folding.name = JSON.parse(response.response).name
            })
            let get_promises_plot_tasks_line_states = [
                new Promise((resolve) => {
                    retrieve_plot_line_states(plot.value.id, settings_store.current_season).then((plot_line_states) => {
                        resolve(plot_line_states)
                    })
                }),
                new Promise((resolve) => {
                    retrieve_plot_season_plot_tasks(plot.value.id, settings_store.current_season).then((plot_tasks) => {
                        resolve(plot_tasks)
                    })
                })
            ]
            Promise.all(get_promises_plot_tasks_line_states).then((results) => {
                let plot_line_states = results[0]
                let plot_tasks = results[1]
                for (let i = 0; i < plot.value.tasks.length; i++) {
                    // Find the corresponding tasks in plot_tasks
                    for (let plot_task of plot_tasks) {
                        if (plot.value.tasks[i].id == plot_task.task) {
                            plot.value.tasks[i].checked = true
                            plot.value.tasks[i].checked_db = true
                            plot.value.tasks[i].plot_task_id = plot_task.id
                            no_tasks_registered.value = false
                            break
                        }
                    }
                }
                for (let i = 0; i < plot.value.tasks.length; i++) {
                    plot.value.tasks[i].line_states = []
                    // Find the corresponding line states in plot_line_states
                    for (let plot_line_state of plot_line_states) {
                        if (plot_line_state.plot_task == plot.value.tasks[i].plot_task_id) {
                            plot.value.tasks[i].line_states.push(plot_line_state)
                        }
                    }
                }
                for (let i = 0; i < plot.value.tasks.length; i++) {
                    // Compute the percentage done for each task
                    plot.value.tasks[i].nb_lines_done = 0
                    for (let line_state of plot.value.tasks[i].line_states) {
                        if (line_state.done)
                            plot.value.tasks[i].nb_lines_done++
                    }
                }
            })
        })
    })

    const update_plot = () => {
        let task_ids = []
        let are_db_tasks_different = false
        for (let task of plot.value.tasks) {
            if (task.checked) {
                task_ids.push(task.id)
            }
            if (task.checked != task.checked_db) {
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
            request_promises.push(
                send_api(
                    "POST",
                    "plots/" + plot.value.id + "/plot_tasks/" + settings_store.current_season,
                    task_ids
                )
            )
        }
        if (has_plot_changed) {
            let plot_data = {
                id: plot.value.id,
                type: "Feature",
                geometry: {
                    type: "Polygon",
                    coordinates: [
                    map_store.regions[0].map((x) => [ x.x, x.y ])
                    ]
                },
                properties: {
                    name: plot.value.name,
                    variety: plot.value.variety.id,
                    pruning: plot.value.pruning.id,
                    folding: plot.value.folding.id
                }
            }
            request_promises.push(send_api("PUT", "plots/" + plot.value.id, plot_data))
        }
        Promise.all(request_promises).then((responses) => {
            let new_plot_tasks = JSON.parse(responses[0].response)
            for (let i = 0; i < plot.value.tasks.length; i++) {
                if (!plot.value.tasks[i].checked_db) {
                    for (let new_plot_task of new_plot_tasks) {
                        if (new_plot_task.task == plot.value.tasks[i].id) {
                            plot.value.tasks[i].plot_task_id = new_plot_task.id
                            plot.value.tasks[i].checked_db = true
                            plot.value.tasks[i].nb_lines_done = 0
                            break
                        }
                    }
                    plot.value.tasks[i].line_states = []
                    for (let line of map_store.lines) {
                        plot.value.tasks[i].line_states.push({
                            line_location: {
                                start: line.start, end: line.end
                            },
                            line: line.id,
                            plot: plot.value.id,
                            task: plot.value.tasks[i].id,
                            season: settings_store.current_season,
                            done: false
                        })
                    }
                }
                plot.value.tasks[i].checked_db = plot.value.tasks[i].checked
            }
            update_display.value = false
        })
    }

    const delete_plot = () => {
        send_api("DELETE", "plots/" + plot.value.id).then((response) => {
            if (response.status == 500) {
                console.error("Could not delete plot #" + plot.value.id + " ...")
            }
            else {
                router.push('/')
            }
        }).catch((error) => {
            console.error("Could not delete plot #" + plot.value.id + " ...")
            console.error(error)
        })
    }

    const start_update = () => {
        update_display.value = true
        plot_backup = clone_plot(plot.value)
    }

    const quit_update = () => {
        update_display.value = false
        plot.value = clone_plot(plot_backup)
    }

    const clone_plot = (in_plot) => {
        let out_plot = Object.assign({}, in_plot)
        out_plot.variety = Object.assign({}, in_plot.variety)
        out_plot.pruning = Object.assign({}, in_plot.pruning)
        out_plot.folding = Object.assign({}, in_plot.folding)
        out_plot.tasks = []
        for (let task of in_plot.tasks) {
            out_plot.tasks.push(Object.assign({}, task))
        }
        return out_plot
    }

    const has_plot_been_modified = () => {
        return !(plot.value.name == plot_backup.name &&
            plot.value.variety.id == plot_backup.variety.id &&
            plot.value.pruning.id == plot_backup.pruning.id &&
            plot.value.folding.id == plot_backup.folding.id
        )
    }

    const select_task = (task_id) => {
        map_store.lines_done = []
        if (task_id == active_task_id.value) {
            active_task_id.value = -1
            map_container.value.redraw()
            return
        }
        active_task_id.value = task_id
        for (let i = 0; i < plot.value.tasks.length; i++) {
            if (task_id == plot.value.tasks[i].plot_task_id) {
                for (let line_state of plot.value.tasks[i].line_states) {
                    if (line_state.done) {
                        map_store.lines_done.push({
                            start: { x: line_state.line_location.start[0], y: line_state.line_location.start[1] },
                            end: { x: line_state.line_location.end[0], y: line_state.line_location.end[1] },
                            id: line_state.line
                        })
                    }
                }
                break
            }
        }
        map_container.value.redraw()
    }
</script>