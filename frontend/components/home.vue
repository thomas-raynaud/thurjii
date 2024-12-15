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
                            <span class="d-block">{{ parcelle.nom }}</span>
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

<script>

import { send_http_request, media_url } from '../lib/request'

export default {
    name: "home",
    data() {
        return {
            parcelles: []
        }
    },
    mounted() {
        send_http_request("GET", "parcelles/").then((response) => {
            if (response.status == 0) {
                console.log("Error when loading parcelles ...")
            }
            else {
                this.parcelles = JSON.parse(response.response)
                this.parcelles.forEach(parcelle => {
                    parcelle.img_src = media_url + parcelle.image + "/"
                })
            }
            
        }).catch((error) => {
            console.log("Error when loading parcelles ...")
            console.log(error)
        })
    }
}
</script>