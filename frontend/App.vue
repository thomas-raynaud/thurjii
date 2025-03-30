<template>
    <div id="app">
        <div class="topnav">
            <router-link to="/">
                <div>
                    <img src="./images/icon_white.ico" width="18px">
                    <p>Home</p>
                </div>
            </router-link>
            <router-link to="/map-sandbox">
                <div>
                    <p>Carte</p>
                </div>
            </router-link>
            <router-link to="/about">
                <div>
                    <p>A propos</p>
                </div>
            </router-link>
        </div>
        <router-view />
    </div>
</template>

<script setup>
    import { onMounted } from 'vue'

    import { send_api } from './lib/request'
    import { data_store } from './stores/data_store'

    onMounted(() => {
        send_api("GET", "saisons").then((response) => {
                let saisons = JSON.parse(response.response)
                if (saisons.length == 0 || saisons[0].fin !== null) {
                    // Ajout d'une nouvelle saison
                    let date = new Date()
                    let year = date.getFullYear()
                    let month = date.getMonth() + 1
                    if (month > 8) // Si en septembre ou après on commence la saison de l'année prochaine
                        year += 1
                    month = (month < 10 ? "0" + month : "" + month)
                    let day = date.getDate()
                    day = (day < 10 ? "0" + day : "" + day)
                    let beginning_season = year + "-" + month + "-" + day
                    send_api("POST", "saisons", { annee : "" + year, debut: beginning_season })
                    .then((response) => {
                        data_store.season = JSON.parse(response.response).annee
                    })
                }
                else {
                    data_store.season = saisons[0].annee
                }
        })
    })


</script>