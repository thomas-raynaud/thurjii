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
    import { onMounted, useTemplateRef, watch, ref } from 'vue'

    import MapContainer from '../components/map_container.vue'
    import { map_store } from '../stores/map_store'
    import { settings_store } from '../stores/settings_store'
    import { STATE } from '../lib/enums'
    import { send_api } from '../lib/request'
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
    const dvpf_map = ref({
        designation: new Map(),
        variety: new Map(),
        pruning: new Map(),
        folding: new Map(),
    })
    const regions_dvpf = ref({
        designation: [],
        variety: [],
        pruning: [],
        folding: [],
    })

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
                        regions_dvpf.value.designation.push(plot.designation)
                        regions_dvpf.value.variety.push(plot.variety)
                        regions_dvpf.value.pruning.push(plot.pruning)
                        regions_dvpf.value.folding.push(plot.folding)
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
                send_api("GET", "designations").then((response) => {
                    let designations = JSON.parse(response.response)
                    for (let designation of designations) {
                        dvpf_map.value.designation.set(designation.id, designation)
                    }
                    resolve()
                })
            }),
            new Promise((resolve) => {
                send_api("GET", "varieties").then((response) => {
                    let varieties = JSON.parse(response.response)
                    for (let variety of varieties) {
                        dvpf_map.value.variety.set(variety.id, variety)
                    }
                    resolve()
                })
            }),
            new Promise((resolve) => {
                send_api("GET", "prunings").then((response) => {
                    let prunings = JSON.parse(response.response)
                    for (let pruning of prunings) {
                        dvpf_map.value.pruning.set(pruning.id, pruning)
                    }
                    resolve()
                })
            }),
            new Promise((resolve) => {
                send_api("GET", "foldings").then((response) => {
                    let foldings = JSON.parse(response.response)
                    for (let folding of foldings) {
                        dvpf_map.value.folding.set(folding.id, folding)
                    }
                    resolve()
                })
            }),
        ]
        Promise.all(get_promises).then(() => {
            let color_prop = DVPF_NAMES[settings_store.plot_color_type]
            map_store.regions_color = new Array(map_store.regions.length)
            for (let i = 0; i < map_store.regions.length; i++) {
                let prop_ind = regions_dvpf.value[color_prop][i]
                let color = dvpf_map.value[color_prop].get(prop_ind).color
                map_store.regions_color[i] = color
            }
            map_container.value.redraw()
        })
    })

    watch(() => map_store.show_plot_names, () => {
        map_container.value.redraw()
    })
</script>