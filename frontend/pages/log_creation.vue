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
            <p v-show="lines_selected > 0"> {{ lines_selected }} rangs sélectionnés</p>
            <div class="row row-cols-auto">
                <div class="col">
                    <button
                        type="button"
                        class="btn btn-primary"
                        @click="create_log()"
                        :disabled="log_data.plot_id==-1"
                    >
                        Créer le log
                    </button>
                </div>
                <div>
                    <button
                        type="button"
                        class="btn btn-light"
                        @click="reset_lines()"
                        :disabled="nb_lines_done == 0"
                    >
                        Réinitialiser tous les rangs
                    </button>
                </div>
            </div>
        </div>
    </div>
    <toast ref="toast_component" />
</template>

<script setup>
    import { ref, onMounted, useTemplateRef, watch, toRaw, computed } from 'vue'

    import MapContainer from '../components/map_container.vue'
    import Toast from '../components/toast.vue'
    import { settings_store } from '../stores/settings_store'
    import { map_store } from '../stores/map_store'
    import { send_api } from '../lib/request'
    import {
        retrieve_plot_season_plot_tasks,
        retrieve_plots,
        retrieve_tasks,
        retrieve_plot_lines,
        retrieve_plot_line_states
    } from '../lib/api_retrieval'
    import { STATE } from '../lib/enums'
    import { compute_plot_array_bb } from '../lib/map_navigation'
    import { fill_regions_dvpf, load_dvpf_map, set_colors } from '../lib/dvpf_colors'

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
    let dvpf_map
    let lines_id_ind_map = new Map()

    const lines_selected = computed(() => {
        return map_store.lines_highlighted.reduce((acc, lh) => { return acc + lh.length }, 0)
    })
    const nb_lines_done = computed(() => {
        return map_store.lines_done.reduce((acc, ld) => { return acc + ld.length }, 0)
    })

    onMounted(() => {
        retrieve_plots().then((in_plots) => {
            plots.value = in_plots
            vineyard_bb = compute_plot_array_bb(in_plots)
            load_dvpf_map().then((in_dvpf_map) => {
                dvpf_map = in_dvpf_map
                configure_map()
                update_map_lines()
            })
            
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
        map_store.regions = []
        map_store.lines = []
        map_store.lines_done = []
        map_store.lines_highlighted = []
        let plot_bb = null
        if (log_data.value.plot_id == -1) {
            map_store.state = STATE.DISPLAY_VINEYARD
            map_store.lines_highlighted = []
            for (let plot of plots.value) {
                let plot_regions = plot.plot_sections.reduce((accumulator, plot_section) => {
                    return accumulator.concat([ plot_section.region ])
                }, [])
                map_store.regions = map_store.regions.concat(plot_regions)
            }
            map_store.show_plot_names = false
            if (plots.value.length > 0) {
                let regions_dvpf = fill_regions_dvpf(plots._rawValue)
                set_colors(dvpf_map, regions_dvpf)
            }
        }
        else {
            map_store.state = STATE.DISPLAY_PLOT
            for (let plot of plots.value) {
                if (plot.id == log_data.value.plot_id) {
                    map_store.regions = plot.plot_sections.reduce((accumulator, plot_section) => {
                        return accumulator.concat([ plot_section.region ])
                    }, [])
                    plot_bb = compute_plot_array_bb([ plot ])
                    let regions_dvpf = fill_regions_dvpf([ toRaw(plot) ])
                    set_colors(dvpf_map, regions_dvpf)
                    break
                }
            }
        }
        empty_lines_arrays()
        if (log_data.value.plot_id == -1)
            map_container.value.center_map_on_region([ vineyard_bb.min, vineyard_bb.max ])
        else {
            map_container.value.center_map_on_region([ plot_bb.min, plot_bb.max ])
        }
    }

    const empty_lines_arrays = () => {
        map_store.lines = []
        map_store.lines_done = []
        map_store.lines_highlighted = []
        for (let i = 0; i < map_store.regions.length; i++) {
            map_store.lines.push([])
            map_store.lines_done.push([])
            map_store.lines_highlighted.push([])
        }
    }

    const update_map_lines = () => {
        return new Promise((resolve) => {
            empty_lines_arrays()
            if (log_data.value.plot_id == -1) {
                resolve()
                return
            }
            retrieve_plot_lines(log_data.value.plot_id).then((lines) => {
                map_store.lines = lines
                lines_id_ind_map.clear()
                for (let i = 0; i < lines.length; i++) {
                    for (let j = 0; j < lines[i].length; j++) {
                        lines_id_ind_map.set(lines[i][j].id, [i, j])
                    }
                }
                if (log_data.value.plot_task_id == -1) {
                    resolve()
                    return
                }
                retrieve_plot_line_states(log_data.value.plot_id, settings_store.current_season).then((line_states) => {
                    for (let line_state of line_states) {
                        if (line_state.plot_task != log_data.value.plot_task_id)
                            continue
                        if (line_state.done) {
                            let section_ind = lines_id_ind_map.get(line_state.line)[0]
                            let line_ind = lines_id_ind_map.get(line_state.line)[1]
                            map_store.lines_done[section_ind].push(
                                map_store.lines[section_ind][line_ind]
                            )
                        }
                    }
                    resolve()
                })
            })
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
            update_map_lines().then(() => { map_container.value.redraw() })
        })
        
    })

    watch(() => log_data.value.plot_task_id, () => {
        if (log_data.value.plot_task_id == -1)
            map_store.state = STATE.DISPLAY_PLOT
        else
            map_store.state = STATE.SELECT_LINES
        update_map_lines().then(() => { map_container.value.redraw() })
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
            let line_states_put_data = []
            for (let lines_section of map_store.lines_highlighted) {
                for (let line_selected of lines_section) {
                    line_states_put_data.push({
                        line: line_selected.id,
                        plot_task: log_data.value.plot_task_id,
                        done: true
                    })
                }
            }
            let post_promises = []
            post_promises.push(send_api("POST", "logs", log_post_data))
            post_promises.push(send_api("PUT", "line_states", line_states_put_data))
            Promise.all(post_promises).then((responses) => {
                if (responses[0].status == 400) {
                    console.error(JSON.parse(responses[0].response))
                    toast_component.value.display_toast("Erreur : le log n'a pas pu être créé")
                    return
                }
                toast_component.value.display_toast("Log créé")
                log_data.value.plot_task_id = -1
                log_data.value.nb_hours =  undefined
                log_data.value.comment = ""
            })
            .catch((errors) => {
                console.error(errors)
                toast_component.value.display_toast("Erreur : le log n'a pas pu être créé")
            })
        }
    }

    const reset_lines = () => {
        let line_states_put_data = []
        for (let lines_section of map_store.lines_done) {
            for (let line_done of lines_section) {
                line_states_put_data.push({
                    line: line_done.id,
                    plot_task: log_data.value.plot_task_id,
                    done: false
                })
            }
        }
        send_api("PUT", "line_states", line_states_put_data)
        .then(() => {
            map_store.lines_done = []
            for (let i = 0; i < map_store.regions.length; i++) {
                map_store.lines_done.push([])
            }
            map_container.value.redraw()
            toast_component.value.display_toast("Rangs réinitialisés")
        })
    }
</script>