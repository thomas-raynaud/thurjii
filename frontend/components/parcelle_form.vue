<template>
    <div class="mb-3">
        <input class="form-control" v-model="formData.nom" placeholder="Nom de la parcelle">
    </div>
    <select-or-create-form
        :form-data="formData.cepage"
        :form-list="cepages"
        form-check-label="Ajouter un nouveau cépage"
        form-new-data-placeholder="Nom du cépage"
    />
    <select-or-create-form
        :form-data="formData.taille"
        :form-list="tailles"
        form-check-label="Ajouter un nouveau type de taille"
        form-new-data-placeholder="Nom du type de taille"
    />
    <select-or-create-form
        :form-data="formData.pliage"
        :form-list="pliages"
        form-check-label="Ajouter un nouveau type de pliage"
        form-new-data-placeholder="Nom du type de pliage"
    />
    <div class="invalid-feedback mb-3" :style="{'display': invalidData ? 'block' : 'none'}">
        Veuillez compléter tous les champs.
    </div>
</template>

<script setup>
    import { defineProps, onMounted, ref } from 'vue'

    import SelectOrCreateForm from '../components/select_or_create_form.vue'
    import { send_api } from '../lib/request'

    const props = defineProps([ 'formData', 'invalidData' ])
    const cepages = ref([])
    const tailles = ref([])
    const pliages = ref([])

    onMounted(() => {
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
</script>