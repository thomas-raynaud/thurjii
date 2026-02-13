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

    import { retrieve_plots } from '../lib/api_retrieval'

    const total_area = ref(0)

    onMounted(() => {
        retrieve_plots().then((plots) => {
            let area = plots.reduce((acc, plot) => { return acc + plot.plot_sections.reduce((acc2, section) => acc2 + section.area, 0) }, 0)
            total_area.value = Math.floor((area / 10000) * 100) / 100
        })
    })
</script>