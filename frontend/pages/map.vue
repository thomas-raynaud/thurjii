<template>
    <div class="row">
        <div class="col">
            <map-container ref="map_container" nb-tiles-x="5" nb-tiles-y="3" />
        </div>
        <div class="col">
            <input class="form-check-input me-1" type="checkbox" v-model="map_store.show_plot_names">
            <label class="form-check-label">Afficher le nom des parcelles</label>
        </div>
    </div>
</template>

<script setup>
    import { onMounted, useTemplateRef, watch } from 'vue'

    import MapContainer from '../components/map_container.vue'
    import { map_store } from '../stores/map_store'
    import { settings_store } from '../stores/map_store'
    import { PLOT_COLOR_TYPES, STATE } from '../lib/enums'
    import { compute_vineyard_bb } from '../lib/map_navigation'
    import { get_polygon_center } from '../lib/geometry'
    import {
        retrieve_plots,
    } from '../lib/api_retrieval'
    import { DVPF_NAMES } from '../lib/const'

    const map_container = useTemplateRef("map_container")
    const designations = ref([])
    const varieties = ref([])
    const prunings = ref([])
    const foldings = ref([])

    onMounted(() => {
        map_store.state = STATE.DISPLAY_VINEYARD
        map_store.regions = []
        map_store.plot_names = []
        map_store.show_plot_names = true
        let get_promises = [
            new Promise((resolve) => {
                retrieve_plots().then((plots) => {
                    for (let plot of plots) {
                        let plot_regions = plot.plot_sections.reduce((accumulator, plot_section) => {
                            return accumulator.concat([ plot_section.region ])
                        }, [])
                        map_store.regions = plot_regions
                        map_store.region_centers.push(get_polygon_center([].concat(...plot_regions)))
                        map_store.plot_names.push(plot.name)
                    }
                    let vineyard_bb = compute_vineyard_bb(plots)
                    if (vineyard_bb != null) {
                        map_container.value.center_map_on_region([ vineyard_bb.min, vineyard_bb.max ])
                    }
                    resolve()
                })
            }),
            new Promise((resolve) => {
                send_api("GET", "designations/").then((response) => {
                    designations.value = JSON.parse(response.response)
                    resolve()
                })
            }),
            new Promise((resolve) => {
                send_api("GET", "varieties/").then((response) => {
                    varieties.value = JSON.parse(response.response)
                    resolve()
                })
            }),
            new Promise((resolve) => {
                send_api("GET", "prunings/").then((response) => {
                    prunings.value = JSON.parse(response.response)
                    resolve()
                })
            }),
            new Promise((resolve) => {
                send_api("GET", "foldings/").then((response) => {
                    foldings.value = JSON.parse(response.response)
                    resolve()
                })
            }),
        ]
        Promise.all(get_promises).then(() => {
            let color_prop = DVPF_NAMES[settings_store.plot_color_type]
            if (settings_store.plot_color_type == PLOT_COLOR_TYPES.DESIGNATION) {
                map_store.regions_color = new Array(map_store.regions.length)
                for (let i = 0; i < map_store.regions.length; i++) {
                    map_store.regions_color[i] = plots[i][DVPF_NAMES[]]
                }
                map_store.regions_color
            }
            map_container.value.redraw()
        })
    })

    watch(() => map_store.show_plot_names, () => {
        map_container.value.redraw()
    })
</script>