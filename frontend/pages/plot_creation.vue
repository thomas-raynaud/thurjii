<template>
    <div class="body row justify-content-center">
        <div class="col-auto">
            <p class="fs-3 text-center" v-show="map_store.state == STATE.SELECT_REGION">Sélectionner une région</p>
            <p class="fs-3 text-center" v-show="map_store.state == STATE.PLACE_LINES">Placer les rangs</p>
            <map-container nb-tiles-x="3" nb-tiles-y="2" />
        </div>
        <div class="col">
            <div class="mb-3">
                <input class="form-control" v-model="plot_data.nom" placeholder="Nom de la parcelle">
            </div>
            <select-or-create-form
                :form-data="plot_data.cepage"
                :form-list="cepages"
                form-check-label="Ajouter un nouveau cépage"
                form-new-data-placeholder="Nom du cépage"
            />
            <select-or-create-form
                :form-data="plot_data.taille"
                :form-list="tailles"
                form-check-label="Ajouter un nouveau type de taille"
                form-new-data-placeholder="Nom du type de taille"
            />
            <select-or-create-form
                :form-data="plot_data.pliage"
                :form-list="pliages"
                form-check-label="Ajouter un nouveau type de pliage"
                form-new-data-placeholder="Nom du type de pliage"
            />
            <div>
                <p v-show="map_store.state == STATE.PLACE_LINES">{{ "Nombre de rangs : " + map_store.lines.length }}</p>
                <p v-show="map_store.state == STATE.PLACE_LINES">{{ "Superficie : " + area_region + " ha"}}</p>
            </div>
            <div class="invalid-feedback mb-3" :style="{'display': invalid_data ? 'block' : 'none'}">
                Veuillez compléter tous les champs.
            </div>
            <button
                class="btn btn-primary"
                :disabled="map_store.state == STATE.SELECT_REGION"
                @click="create_plot()"
            >
                Créer la parcelle
            </button>
        </div>
    </div>
</template>

<script setup>
    import { computed, ref, onMounted, toRaw } from 'vue'
    import { useRouter } from 'vue-router'

    import MapContainer from '../components/map_container.vue'
    import SelectOrCreateForm from '../components/select_or_create_form.vue'
    import { map_store } from '../stores/map_store'
    import { get_area } from '../lib/geometry'
    import { get_map_coords, from_rel_coords_to_mercator } from '../lib/map_navigation'
    import { STATE } from '../lib/enums'
    import { send_api } from '../lib/request'

    const router = useRouter()

    const plot_data = ref({
        nom: "",
        cepage: { id: -1, nom: "" },
        taille: { id: -1, nom: "" },
        pliage: { id: -1, nom: "" }
    })
    const cepages = ref([])
    const tailles = ref([])
    const pliages = ref([])
    const invalid_data = ref(false)

    onMounted(() => {
        map_store.state = STATE.SELECT_REGION
        map_store.region = []
        map_store.lines = []
        // Load cepages
        send_api("GET", "cepages").then((response) => {
            cepages.value = JSON.parse(response.response)
        }).catch((error) => {
            console.error("Error when loading cepages ...")
            console.error(error)
        })
        // Load tailles
        send_api("GET", "tailles").then((response) => {
            tailles.value = JSON.parse(response.response)
        }).catch((error) => {
            console.error("Error when loading tailles ...")
            console.error(error)
        })
        // Load pliages
        send_api("GET", "pliages").then((response) => {
            pliages.value = JSON.parse(response.response)
        }).catch((error) => {
            console.error("Error when loading pliages ...")
            console.error(error)
        })
    })

    const area_region = computed(() => {
        let area = get_area(map_store.region)
        let area_h = area / 10000
        return Math.floor(area_h * 100) / 100
    })

    const create_plot = () => {
        invalid_data.value = plot_data.value.nom == ""
            || plot_data.value.cepage.nom == ""
            || plot_data.value.taille.nom == ""
            || plot_data.value.pliage.nom == ""
        if (invalid_data.value)
            return
        let region = toRaw(map_store.region)
        region = region.map((x) => [ x.x, x.y ])
        // GEOJson format
        const plot_data_req = {
            type: "Feature",
            geometry: {
                type: "Polygon",
                coordinates: [ region ]
            },
            properties: {
                nom: plot_data.value.nom,
                cepage: plot_data.value.cepage.id,
                taille: plot_data.value.taille.id,
                pliage: plot_data.value.pliage.id
            }
        }
        let post_promises = []
        if (plot_data.value.cepage.id == -1) {
            post_promises.push(new Promise((resolve, reject) => {
                send_api("POST", "cepages", { nom: plot_data.value.cepage.nom })
                .then((response) => {
                    plot_data_req.properties.cepage = JSON.parse(response.response).id
                    resolve()
                })
                .catch((error) => { reject(error) })
            }))
        }
        if (plot_data.value.taille.id == -1) {
            post_promises.push(new Promise((resolve, reject) => {
                send_api("POST", "tailles", { nom: plot_data.value.taille.nom })
                .then((response) => {
                    plot_data_req.properties.taille = JSON.parse(response.response).id
                    resolve()
                })
                .catch((error) => { reject(error) })
            }))
        }
        if (plot_data.value.pliage.id == -1) {
            post_promises.push(new Promise((resolve, reject) => {
                send_api("POST", "pliages", { nom: plot_data.value.pliage.nom })
                .then((response) => {
                    plot_data_req.properties.pliage = JSON.parse(response.response).id
                    resolve()
                })
                .catch((error) => { reject(error) })
            }))
        }
        Promise.all(post_promises).then(() => {
            map_store.lines
            send_api("POST", "parcelles", plot_data_req)
            .then((response) => {
                let parcelle = JSON.parse(response.response)
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
                        parcelle: parcelle.id,
                        location: {
                            type: "LineString",
                            coordinates: line_mc
                        }
                    })
                }
                send_api("POST", "rangs", lines_data_req)
                .then((response) => {
                    router.push('parcelles/' + parcelle.id)
                })
                .catch((error) => {
                    console.error("Could not create lines associated to plot " + parcelle.id + " ...")
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