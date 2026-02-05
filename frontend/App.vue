<template>
    <div id="app">
        <div class="topnav">
            <router-link to="/">
                <div>
                    <img src="./images/icon_white.ico" width="18px">
                    <p>Home</p>
                </div>
            </router-link>
            <router-link to="/logs">
                <div>
                    <p>Logs</p>
                </div>
            </router-link>
            <router-link to="/map">
                <div>
                    <p>Carte</p>
                </div>
            </router-link>
            <router-link to="/statistics">
                <div>
                    <p>Statistiques</p>
                </div>
            </router-link>
            <router-link to="/settings">
                <div>
                    <p>Paramètres</p>
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

    import { get_current_season } from './lib/api_retrieval'
    import { settings_store } from './stores/settings_store'

    onMounted(() => {
        get_current_season().then((current_season) => {
            settings_store.current_season = current_season
        })

        let color_type = $cookies.get("color_type")
        settings_store.plot_color_type = (color_type == null ? 1 : parseInt(color_type))
    })


</script>