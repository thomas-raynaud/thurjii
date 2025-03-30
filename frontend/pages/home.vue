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
                                @click="$router.push('creation-parcelle')"
                            >
                                Ajouter une parcelle
                            </button>
                        </div>
                    </div>
                    <div class="row row-cols-4">
                        <div class="col"
                            v-for="parcelle in parcelles"
                            :key="parcelle.id"
                        >
                            <div class="card">
                                <div class="card-img-top d-flex justify-content-center img-container">
                                    <map-display
                                        ref="map_displays" 
                                        nb-tiles-x="1" nb-tiles-y="1"
                                    />
                                    <!--<img :src="parcelle.img_src" height="256px" class="card-img-top" />-->
                                </div>
                                <div class="card-body">
                                    <h5 class="card-title">{{ parcelle.nom }}</h5>
                                    <button class="btn btn-primary" @click="$router.push('parcelles/' + parcelle.id)">Voir détails</button>
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
    .img-container {
        height: 256px;
        background-color: black;
        z-index: 1;
    }
</style>

<script setup>
    import { ref, onMounted, nextTick } from 'vue'

    import MapDisplay from '../components/map_display.vue'
    import { send_api, MEDIA_URL } from '../lib/request'
    import {
        get_region_center_params
    } from '../lib/map_navigation'

    const parcelles = ref([])
    const map_displays = ref([])

    onMounted(() => {
        load_plots()
    })

    const load_plots = () => {
        send_api("GET", "parcelles").then((response) => {
            if (response.status == 0) {
                console.error("Error when loading plots ...")
            }
            else {
                let parcelles_api = JSON.parse(response.response).features
                parcelles.value = []
                parcelles_api.forEach(parcelle_api => {
                    let parcelle = parcelle_api.properties
                    parcelle.id = parcelle_api.id
                    parcelle.region = parcelle_api.geometry.coordinates[0].map((x) => { return { x: x[0], y: x[1] }})
                    parcelle.img_src = MEDIA_URL + parcelle.image + "/"
                    parcelles.value.push(parcelle)
                })
                nextTick(() => {
                    for (let i = 0; i < parcelles.value.length; i++) {
                        let center_params = get_region_center_params(parcelles.value[i].region, [ 1, 1 ])
                        map_displays.value[i].position_map(center_params.pos, center_params.zoom, { x: 0.5, y: 0.5 })
                    }
                })
            }
            
        }).catch((error) => {
            console.error("Error when loading plots ...")
            console.error(error)
        })
    }
</script>