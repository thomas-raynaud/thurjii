<template>
    <div class="body row">
        <div class="col-8">
            <div class="card">
                <div class="card-body">
                    <div class="row align-items-center mb-3">
                        <div class="col-md-auto">
                            <h3>Les parcelles</h3>
                        </div>
                        <div class="col">
                            <button
                                type="button" class="btn btn-light"
                                @click="$router.push('plot-creation')"
                            >
                                Ajouter une parcelle
                            </button>
                        </div>
                    </div>
                    <div class="row row-cols-4">
                        <div class="col card-plot-container"
                            v-for="plot in plots"
                            :key="plot.id"
                        >
                            <div class="card card-plot">
                                <div class="card-img-top d-flex justify-content-center img-container">
                                    <map-display
                                        ref="map_displays" 
                                        nb-tiles-x="1" nb-tiles-y="1"
                                    />
                                </div>
                                <div class="card-body">
                                    <h5 class="card-title">{{ plot.name }}</h5>
                                    <button class="btn btn-primary" @click="$router.push('plots/' + plot.id)">Voir détails</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-4">
            <div class="card">
                <div class="card-body">
                    <h3 class="card-title">Rappels</h3>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
    .card-plot-container {
        margin: 0 0.5rem;
    }
    .card-plot {
        width: 258px;
        margin: 0 1rem;
    }
    .img-container {
        height: 256px;
        background-color: black;
        z-index: 1;
    }
</style>

<script setup>
    import { ref, onMounted, nextTick } from 'vue'

    import MapDisplay from '../components/map_display.vue'
    import { get_region_center_params } from '../lib/map_navigation'
    import { retrieve_plots } from '../lib/api_retrieval'

    const plots = ref([])
    const map_displays = ref([])

    onMounted(() => {
        load_plots()
    })

    const load_plots = () => {
        retrieve_plots().then((in_plots) => {
            plots.value = in_plots
            nextTick(() => {
                for (let i = 0; i < plots.value.length; i++) {
                    let plot_points = plots.value[i].plot_sections.reduce((accumulator, plot_section) => {
                        return accumulator.concat(plot_section.region)
                    }, [])
                    let center_params = get_region_center_params(plot_points, [ 1, 1 ])
                    map_displays.value[i].position_map(center_params.pos, center_params.zoom, { x: 0.5, y: 0.5 })
                }
            })
        })
        
    }
</script>