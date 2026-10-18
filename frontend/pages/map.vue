<template>
    <div class="row">
        <div class="col">
            <map-container ref="map_container" nb-tiles-x="5" nb-tiles-y="3" />
        </div>
        <div class="col">
            <input class="form-check-input me-1" type="checkbox" v-model="map_store.show_plot_names">
            <label class="form-check-label">Afficher le nom des parcelles</label>
            <div class="row">
                <div class="col-auto">
                    <p>Coloration des parcelles en fonction de :</p>
                </div>
                <div class="col">
                    <select class="form-control" v-model="settings_store.plot_color_type">
                        <option v-for="color_type in color_types" :value="color_type.id">{{ color_type.name }}</option>
                    </select>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { onMounted, useTemplateRef, watch, ref } from 'vue'

    import MapContainer from '../components/map_container.vue'
    import { settings_store } from '../stores/settings_store'
    import { map_store } from '../stores/map_store'
    import { DVPF_NAMES_FR } from '../lib/const'
    import { STATE, PLOT_COLOR_TYPES } from '../lib/enums'
    
    import { compute_plot_array_bb } from '../lib/map_navigation'
    import { get_polygon_center } from '../lib/geometry'
    import {
        retrieve_plots,
    } from '../lib/api_retrieval'
    import { fill_regions_dvpf, load_dvpf_map, set_colors } from '../lib/dvpf_colors'
    

    const map_container = useTemplateRef("map_container")
    const color_types = ref([])
    const regions_dvpf = ref([])
    const dvpf_map = ref({})

    onMounted(() => {
        map_store.state = STATE.DISPLAY_VINEYARD
        map_store.regions = []
        map_store.plot_names = []
        map_store.region_centers = []
        map_store.show_plot_names = true
        retrieve_plots().then((plots) => {
            for (let plot of plots) {
                let plot_regions = plot.plot_sections.reduce((accumulator, plot_section) => {
                    return accumulator.concat([ plot_section.region ])
                }, [])
                map_store.regions = map_store.regions.concat(plot_regions)
                map_store.region_centers.push(get_polygon_center([].concat(...plot_regions)))
                map_store.plot_names.push(plot.name)
            }
            let vineyard_bb = compute_plot_array_bb(plots)
            if (vineyard_bb != null) {
                map_container.value.center_map_on_region([ vineyard_bb.min, vineyard_bb.max ])
            }
            regions_dvpf.value = fill_regions_dvpf(plots)
            load_dvpf_map().then((in_dvpf_map) => {
                dvpf_map.value = in_dvpf_map
                set_colors(dvpf_map.value, regions_dvpf.value)
                map_container.value.redraw()
            })
        })
        // Load color types
        for (let i = 0; i < PLOT_COLOR_TYPES.LENGTH; i++) {
            color_types.value.push({
                id: i,
                name: DVPF_NAMES_FR[i]
            })
        }
    })

    watch(() => map_store.show_plot_names, () => {
        map_container.value.redraw()
    })

    watch(() => settings_store.plot_color_type, () => {
        set_colors(dvpf_map.value, regions_dvpf.value)
        map_container.value.redraw()
        $cookies.set("color_type", settings_store.plot_color_type)
    })
</script>

<style scoped>
    p {
        margin: 0.5rem 0
    }
</style>