<template>
    <div class="body row justify-content-center">
        <div class="col-auto"
                :style="{
                    width: TILE_SIZE * nb_tiles_x + 'px',
                    height: TILE_SIZE * nb_tiles_y + 'px',
                    padding: '0px',
                    'margin-left': '10px',
                }">
            <map-container ref="map_container" :nb-tiles-x="nb_tiles_x" :nb-tiles-y="nb_tiles_y" class="mb-3" />
            <map-state-controller v-show="map_store.current_region_ind != -1" />
        </div>
        <div class="col">
            <plot-form ref="plot_form"
                :form-data="plot_data"
                :invalid-data="invalid_data"
                :invalid-data-message="invalid_data_message"
            />
            <div>
                <p>{{ "Nombre de rangs total : " + nb_lines_total }}</p>
            </div>
            <button
                class="btn btn-primary"
                :disabled="map_store.state == STATE.ADD_PLOT_SECTION"
                @click="create_plot()"
            >
                Créer la parcelle
            </button>
        </div>
    </div>
</template>

<script setup>
    import { ref, onMounted, toRaw, useTemplateRef, watch, computed } from 'vue'
    import { useRouter } from 'vue-router'

    import MapContainer from '../components/map_container.vue'
    import MapStateController from '../components/map_state_controller.vue'
    import PlotForm from '../components/plot_form.vue'
    import { map_store } from '../stores/map_store'
    import { settings_store } from '../stores/settings_store'
    import { get_map_coords, from_rel_coords_to_mercator, compute_vineyard_bb, TILE_SIZE } from '../lib/map_navigation'
    import { log_error } from '../lib/log'
    import { STATE } from '../lib/enums'
    import { send_api } from '../lib/request'
    import { retrieve_plots, retrieve_tasks } from '../lib/api_retrieval'

    const router = useRouter()

    const plot_data = ref({
        name: "",
        designation: { id: -1, name: "" },
        variety: { id: -1, name: "" },
        pruning: { id: -1, name: "" },
        folding: { id: -1, name: "" },
        tasks: [],
        plot_sections: [],
    })
    const invalid_data = ref(false)
    const invalid_data_message = ref("")
    const plot_form = useTemplateRef("plot_form")
    const map_container = useTemplateRef("map_container")
    let vineyard_bb = []
    const nb_tiles_x = ref("3")
    const nb_tiles_y = ref("2")

    const nb_lines_total = computed(() => {
        return map_store.lines.reduce((accumulator, lines_section) => {
            return accumulator + lines_section.length
        }, 0)
    })

    onMounted(() => {
        map_store.state = STATE.DISPLAY_VINEYARD
        map_store.regions = []
        map_store.lines = []
        map_store.lines_done = []
        map_store.lines_highlighted = []
        map_store.current_region_ind = -1

        retrieve_plots().then((plots_api) => {
            vineyard_bb = compute_vineyard_bb(plots_api)
            if (vineyard_bb != null) {
                map_container.value.center_map_on_region([ vineyard_bb.min, vineyard_bb.max ])
            }
        })
        retrieve_tasks().then((tasks_api) => {
            plot_data.value.tasks = tasks_api
            for (let i = 0; i < plot_data.value.tasks.length; i++) {
                plot_data.value.tasks[i].checked = false
            }
        })
    })

    const create_plot = () => {
        invalid_data.value = plot_data.value.name == ""
            || plot_data.value.designation.name == ""
            || plot_data.value.variety.name == ""
            || plot_data.value.pruning.name == ""
            || plot_data.value.folding.name == ""
        let is_plot_section_name_blank = false
        for (let i = 0; i < plot_data.value.plot_sections.length; i++) {
            if (plot_data.value.plot_sections[i].name == "") {
                is_plot_section_name_blank = true
                break
            }
        }
        invalid_data.value = invalid_data.value || (plot_data.value.plot_sections.length > 1 && is_plot_section_name_blank)
        if (invalid_data.value) {
            invalid_data_message.value = "Veuillez compléter tous les champs."
            return
        }
        let error = { message: "" }
        plot_form.value.check_unique_designation_variety_pruning_folding_name(error)
        if (error.message != "") {
            invalid_data.value = true
            invalid_data_message.value = error.message
            return
        }

        const create_plot_promise = async (plot_name, dvpf_res) => {
            const plot_data_req = {
                name: plot_name,
                designation:    dvpf_res[0],
                variety:        dvpf_res[1],
                pruning:        dvpf_res[2],
                folding:        dvpf_res[3]
            }
            return send_api("POST", "plots", plot_data_req)
        }

        const create_plot_sections_promise = async (plot_sections_data, plot_id) => {
            let regions = toRaw(map_store.regions)
            let plot_sections_data_req = []
            for (let i = 0; i < regions.length; i++) {
                let region = regions[i].map((x) => [ x.x, x.y ])
                // GEOJson format
                plot_sections_data_req.push(
                    {
                        type: "Feature",
                        geometry: {
                            type: "Polygon",
                            coordinates: [ region ]
                        },
                        properties: {
                            name: plot_sections_data[i].name,
                            plot: plot_id
                        },
                    }
                )
            }
            return send_api("POST", "plots/" + plot_id + "/sections", plot_sections_data_req)
        }

        const create_tasks_promise = async (plot_tasks_data, plot_id) => {
            let task_ids = []
            for (let task of plot_tasks_data) {
                if (task.checked) {
                    task_ids.push(task.id)
                }
            }
            return send_api("POST", "plots/" + plot_id + "/plot_tasks/" + settings_store.current_season, task_ids)
        }

        const create_lines_promise = async (plot_id, plot_sections_data) => {
            let lines_data_req = []
            for(let i = 0; i < plot_sections_data.length; i++) {
                for (let j = 0; j < map_store.lines[i].length; j++) {
                    // Convert line coordinates from canvas space to mercator coords
                    let line_mc = map_store.lines[i][j].map((point) => {
                        return [ point.x, point.y ]
                    })
                    lines_data_req.push({
                        type: "Feature",
                        geometry: {
                            type: "LineString",
                            coordinates: line_mc
                        },
                        properties: {
                            plot_section: plot_sections_data[i].id
                        }
                    })
                }
            }
            return send_api("POST", "plots/" + plot_id + "/lines/" + settings_store.current_season, lines_data_req)
        }

        let dvpf_post_promises = plot_form.value.create_designation_variety_pruning_folding()
        Promise.all(dvpf_post_promises).then((dvpf_res) => {
            create_plot_promise(plot_data.value.name, dvpf_res).then((plot_res) => {
                let plot_id = JSON.parse(plot_res.response).id
                let plot_sections_tasks_post_promises = [
                    create_plot_sections_promise(plot_data.value.plot_sections, plot_id),
                    create_tasks_promise(plot_data.value.tasks, plot_id),
                ]
                Promise.all(plot_sections_tasks_post_promises).then((plot_sections_tasks_res) => {
                    let plot_sections_res = JSON.parse(plot_sections_tasks_res[0].response)
                    create_lines_promise(plot_id, plot_sections_res).then(() => {
                        router.push('plots/' + plot_id)
                    }).catch((error) => { log_error("Error: could not create lines associated to plot " + plot_id + "...", error) })
                }).catch((errors) => { log_error("Error: could not create sections/tasks associated to plot " + plot_id + "...", errors) })
            }).catch((error) => { log_error("Error: could not create plot ...", error) })
        }).catch((errors) => { log_error("Error: could not create designation/variety/pruning/folding ...", errors) })
    }

    watch(() => map_store.current_region_ind, (plot_section_selected) => {
        map_store.state = STATE.DISPLAY_VINEYARD
        if (plot_section_selected != -1) {
            if (map_store.regions[plot_section_selected].length == 0)
                map_store.state = STATE.ADD_PLOT_SECTION
        }
        // Recenter map
        let plot_points = map_store.regions.reduce((accumulator, region) => {
            return accumulator.concat(region)
        }, [])
        if (plot_section_selected == -1) {
            if (plot_points.length > 0) {
                map_container.value.center_map_on_region(plot_points)
            }
        }
        else {
            if (map_store.regions[plot_section_selected].length > 0) {
                map_container.value.center_map_on_region(map_store.regions[plot_section_selected])
            }
            else if (plot_points.length > 0) {
                map_container.value.center_map_on_region(plot_points)
            }
        }
    })
</script>