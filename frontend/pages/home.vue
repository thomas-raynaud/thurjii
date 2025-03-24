<template>
    <div class="body row">
        <div class="col-8">
            <div class="card">
                <div class="row align-items-center">
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
                <div class="row">
                    <div class="col">
                        <div class="parcelle container"
                            v-for="parcelle in parcelles"
                            :key="parcelle.id"
                        >
                            <img :src="parcelle.img_src" height="180px" />
                            <span class="d-block" @click="$router.push('parcelles/' + parcelle.id)">{{ parcelle.nom }}</span>
                            <button
                                type="button" class="btn btn-outline-dark"
                                @click="delete_plot(parcelle.id)"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-4">
            <div class="card">
                <h2>Rappels</h2>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, onMounted } from 'vue'

    import { send_http_request, MEDIA_URL } from '../lib/request'

    const parcelles = ref([])

    onMounted(() => {
        load_plots()
    })

    const load_plots = () => {
        send_http_request("GET", "parcelles").then((response) => {
            if (response.status == 0) {
                console.error("Error when loading plots ...")
            }
            else {
                let parcelles_api = JSON.parse(response.response).features
                parcelles.value = []
                parcelles_api.forEach(parcelle_api => {
                    let parcelle = parcelle_api.properties
                    parcelle.id = parcelle_api.id
                    parcelle.region = parcelle_api.geometry.coordinates[0]
                    parcelle.img_src = MEDIA_URL + parcelle.image + "/"
                    parcelles.value.push(parcelle)
                })
            }
            
        }).catch((error) => {
            console.error("Error when loading plots ...")
            console.error(error)
        })
    }

    const delete_plot = (plot_id) => {
        send_http_request("DELETE", "parcelles/" + plot_id).then((response) => {
            if (response.status == 500) {
                console.error("Could not delete plot #" + plot_id + " ...")
            }
            else {
                load_plots()
            }
            load_plots()
        }).catch((error) => {
            console.error("Could not delete plot #" + plot_id + " ...")
            console.error(error)
        })
    }
</script>