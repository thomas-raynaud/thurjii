<template>
    <div class="body row justify-content-center">
        <div class="col-auto">
            <p class="fs-3 text-center" v-show="map_store.state == STATE.DRAW_REGION">Sélectionner une région</p>
            <p class="fs-3 text-center" v-show="map_store.state == STATE.PLACE_LINES">Placer les rangs</p>
            <map-container ref="map_container" nb-tiles-x="3" nb-tiles-y="2" />
        </div>
        <div class="col">
            <plot-form :form-data="plot_data" :invalid-data="invalid_data" :invalid-data-message="invalid_data_message" ref="plot_form" />
            <div>
                <p v-show="map_store.state == STATE.PLACE_LINES">{{ "Nombre de rangs : " + map_store.lines.length }}</p>
            </div>
            <button
                class="btn btn-primary"
                :disabled="map_store.state == STATE.DRAW_REGION"
                @click="create_plot()"
            >
                Créer la parcelle
            </button>
        </div>
    </div>
</template>

<script setup>
    import { ref, onMounted, toRaw, useTemplateRef } from 'vue'
    import { useRouter } from 'vue-router'

    import MapContainer from '../components/map_container.vue'
    import PlotForm from '../components/plot_form.vue'
    import { map_store } from '../stores/map_store'
    import { settings_store } from '../stores/settings_store'
    import { get_map_coords, from_rel_coords_to_mercator, compute_vineyard_bb } from '../lib/map_navigation'
    import { STATE } from '../lib/enums'
    import { send_api } from '../lib/request'
    import { retrieve_plots, retrieve_tasks } from '../lib/api_retrieval'

    const router = useRouter()

    const plot_data = ref({
        name: "",
        variety: { id: -1, name: "" },
        pruning: { id: -1, name: "" },
        folding: { id: -1, name: "" },
        tasks: []
    })
    const invalid_data = ref(false)
    const invalid_data_message = ref("")
    const plot_form = useTemplateRef("plot_form")
    const map_container = useTemplateRef("map_container")

    onMounted(() => {
        map_store.state = STATE.DRAW_REGION
        map_store.regions = [ [] ]
        map_store.lines = []

        retrieve_plots().then((plots_api) => {
            let vineyard_bb = compute_vineyard_bb(plots_api)
            map_container.value.center_map_on_region([ vineyard_bb.min, vineyard_bb.max ])
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
            || plot_data.value.variety.name == ""
            || plot_data.value.pruning.name == ""
            || plot_data.value.folding.name == ""
        if (invalid_data.value) {
            invalid_data_message.value = "Veuillez compléter tous les champs."
            return
        }
        let error = { message: "" }
        plot_form.value.check_unique_variety_pruning_folding_name(error)
        if (error.message != "") {
            invalid_data.value = true
            invalid_data_message.value = error.message
            return
        }
        let region = toRaw(map_store.regions.at(-1))
        region = region.map((x) => [ x.x, x.y ])
        // GEOJson format
        const plot_data_req = {
            type: "Feature",
            geometry: {
                type: "Polygon",
                coordinates: [ region ]
            },
            properties: {
                name: plot_data.value.name,
                variety: plot_data.value.variety.id,
                pruning: plot_data.value.pruning.id,
                folding: plot_data.value.folding.id
            }
        }
        let post_promises = plot_form.value.create_variety_pruning_folding()
        Promise.all(post_promises).then((post_responses) => {
            plot_data_req.properties.variety = post_responses[0]
            plot_data_req.properties.pruning = post_responses[1]
            plot_data_req.properties.folding = post_responses[2]
            send_api("POST", "plots", plot_data_req)
            .then((response) => {
                let plot = JSON.parse(response.response)
                let lines_data_req = []
                for (let i = 0; i < map_store.lines.length; i++) {
                    // Convert line coordinates from canvas space to mercator coords
                    let line_mc = []
                    for (let pos of [ "start", "end" ]) {
                        let p_rel_coords = get_map_coords(map_store.coords, map_store.offset_display, [ map_store.lines[i][pos].x, map_store.lines[i][pos].y ])
                        let p_mc = from_rel_coords_to_mercator(p_rel_coords.x, p_rel_coords.y)
                        line_mc.push([ p_mc.x, p_mc.y ])
                    }
                    lines_data_req.push({
                        plot: plot.id,
                        location: {
                            type: "LineString",
                            coordinates: line_mc
                        }
                    })
                }
                let post_promises_lines_tasks = []
                post_promises_lines_tasks.push(send_api("POST", "plots/" + plot.id + "/lines/" + settings_store.current_season, lines_data_req))
                let task_ids = []
                for (let task of plot_data.value.tasks) {
                    if (task.checked) {
                        task_ids.push(task.id)
                    }
                }
                post_promises_lines_tasks.push(send_api("POST", "plots/" + plot.id + "/plot_tasks/" + settings_store.current_season, task_ids))
                Promise.all(post_promises_lines_tasks).then(() => {
                    router.push('plots/' + plot.id)
                })
                .catch((error) => {
                    console.error("Could not create lines associated to plot " + plot.id + " ...")
                    console.error(error)
                })
            })
            .catch((error) => {
                console.error("Could not create plot ...")
                console.error(error)
            })
        })
        .catch((errors) => {
            console.error(errors)
        })
    }
</script>