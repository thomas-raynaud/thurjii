<template>
    <div class="body row">
        <h2>Paramètres</h2>
        <div class="row">
            <div class="col-auto">
                <p>Couleur utilisée pour les parcelles :</p>
            </div>
            <div class="col">
                <select class="form-control" v-model="settings_store.plot_color_type">
                    <option v-for="color_type in color_types" :value="color_type.id">{{ color_type.name }}</option>
                </select>
            </div>
            
        </div>
    </div>
</template>

<script setup>
    import { onMounted, ref, watch } from 'vue'

    import { DVPF_NAMES_FR } from '../lib/const'
    import { PLOT_COLOR_TYPES } from '../lib/enums'
    import { settings_store } from '../stores/settings_store'

    const color_types = ref([])

    onMounted(() => {
        for (let i = 0; i < PLOT_COLOR_TYPES.LENGTH; i++) {
            color_types.value.push({
                id: i,
                name: DVPF_NAMES_FR[i]
            })
        }
    })

    watch(() => settings_store.plot_color_type, () => {
        $cookies.set("color_type", settings_store.plot_color_type)
    })
</script>

<style scoped>
    p {
        margin: 0.5rem 0
    }
</style>