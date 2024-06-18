<template>
    <div>
        <div class="row">
            <div class="leftcolumn" style="width: 75%;">
                <div class="card">
                    <h2>Les parcelles</h2>
                    <div class="row">
                        <div class="col">
                            <div class="parcelle"
                                v-for="parcelle in parcelles"
                                :key="parcelle.id"
                            >
                                <!--<img src="../images/thumbnails/raytracing_thumb.png" height="180px" />-->
                                <h3>{{ parcelle.nom }}</h3>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="rightcolumn" style="width: 25%;">
                <div class="card">
                    <h2>Rappels</h2>
                </div>
            </div>
        </div>
    </div>
</template>

<script>

import { send_http_request } from '../lib/request'

export default {
    name: "home",
    data() {
        return {
            parcelles: []
        }
    },
    mounted() {
        send_http_request("GET", "parcelles/").then((response) => {
            this.parcelles = JSON.parse(response.response)
        }).catch((error) => {
            console.log("Error when loading parcelles ...")
        })
    }
}
</script>