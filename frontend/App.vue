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
    import { send_http_request } from './lib/request'

    onMounted(() => {
        send_http_request("GET", "saisons").then((response) => {
                let saisons = JSON.parse(response.response)
                console.log(saisons)
                if (saisons.length == 0)
                    add_season()
        })
    })
</script>