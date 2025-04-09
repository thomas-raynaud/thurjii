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
    <div class="card mb-3">
        <div class="card-body">
            <h5>Tâches</h5>
            <ul class="list-group mb-2">
                <li class="list-group-item" v-for="tache in formData.taches">
                    <input class="form-check-input me-1" type="checkbox" :value="tache.checked">
                    <label class="form-check-label">{{ tache.nom }}</label>
                </li>
            </ul>
            <div class="row align-items-center mb-3">
                <div class="col-md-auto">
                    <p class="mb-0">Autre :</p>
                </div>
                <div class="col">
                    <input class="form-control" v-model="new_task_name" placeholder="Nom de la tâche">
                </div>
                <div class="col">
                    <button
                        type="button" class="btn btn-light"
                        @click="add_task()"
                    >
                        Ajouter
                    </button>
                </div>
            </div>
            <div class="invalid-feedback mb-3" :style="{'display': task_name_empty ? 'block' : 'none'}">
                Veuillez saisir le nom de la tâche.
            </div>
            <div class="invalid-feedback mb-3" :style="{'display': task_name_already_exists ? 'block' : 'none'}">
                Cette tâche existe déjà.
            </div>
        </div>
    </div>
    
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
    const new_task_name = ref("")
    const task_name_empty = ref(false)
    const task_name_already_exists = ref(false)

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

    const add_task = () => {
        if (new_task_name.value == "") {
            task_name_empty.value = true
            return
        }
        task_name_empty.value = false
        send_api("POST", "taches", { nom: new_task_name.value })
        .then((response) => {
            if (response.status == 400) {
                task_name_already_exists.value = true
            }
            else {
                let tache = JSON.parse(response.response)
                tache.checked = true
                props.formData.taches.push(tache)
                task_name_already_exists.value = false
                new_task_name.value = ""
            }
            
        })
        .catch((error) => { console.error(error) })
    }

    const create_cepage_taille_pliage = () => {
        let post_promises = []
        if (props.formData.cepage.id == -1) {
            post_promises.push(new Promise((resolve, reject) => {
                send_api("POST", "cepages", { nom: props.formData.cepage.nom })
                .then((response) => {
                    resolve(JSON.parse(response.response).id)
                })
                .catch((error) => { reject(error) })
            }))
        }
        else {
            post_promises.push(new Promise((resolve) => { resolve(props.formData.cepage.id) }))
        }
        if (props.formData.taille.id == -1) {
            post_promises.push(new Promise((resolve, reject) => {
                send_api("POST", "tailles", { nom: props.formData.taille.nom })
                .then((response) => {
                    resolve(JSON.parse(response.response).id)
                })
                .catch((error) => { reject(error) })
            }))
        }
        else {
            post_promises.push(new Promise((resolve) => { resolve(props.formData.taille.id) }))
        }
        if (props.formData.pliage.id == -1) {
            post_promises.push(new Promise((resolve, reject) => {
                send_api("POST", "pliages", { nom: props.formData.pliage.nom })
                .then((response) => {
                    resolve(JSON.parse(response.response).id)
                })
                .catch((error) => { reject(error) })
            }))
        }
        else {
            post_promises.push(new Promise((resolve) => { resolve(props.formData.pliage.id) }))
        }
        return post_promises
    }

    defineExpose({
        create_cepage_taille_pliage
    })
</script>