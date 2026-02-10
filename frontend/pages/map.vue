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
    import { STATE } from '../lib/enums'
    
    import { compute_plot_array_bb } from '../lib/map_navigation'
    import { get_polygon_center } from '../lib/geometry'
    import {
        retrieve_plots,
    } from '../lib/api_retrieval'
    import { fill_regions_dvpf, load_dvpf_map, set_colors } from '../lib/dvpf_colors'
    

    const map_container = useTemplateRef("map_container")

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
            let regions_dvpf = fill_regions_dvpf(plots)
            load_dvpf_map().then((dvpf_map) => {
                set_colors(dvpf_map, regions_dvpf)
                map_container.value.redraw()
            })
        })

    })

    watch(() => map_store.show_plot_names, () => {
        map_container.value.redraw()
    })
</script>