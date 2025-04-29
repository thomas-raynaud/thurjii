<template>
    <div class="body row">
        <h2>Statistiques</h2>
        <div class="row">
            <p>Surface totale de l'exploitation : {{ total_area }} ha</p>
        </div>
    </div>
</template>

<script setup>
    import { ref, onMounted } from 'vue'

    import { send_api } from '../lib/request'

    const total_area = ref(0)

    onMounted(() => {
        send_api("GET", "parcelles").then((response) => {
            let parcelles = JSON.parse(response.response).features
            let area = parcelles.reduce((accumulator, parcelle) => accumulator + parcelle.properties.area, 0)
            total_area.value = Math.floor((area / 10000) * 100) / 100
        })
    })
</script>