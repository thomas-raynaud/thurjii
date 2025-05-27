<template>
    <div class="mb-3">
        <input class="form-control" v-model="formData.name" placeholder="Nom de la parcelle">
    </div>
    <select-or-create-form
        :form-data="formData.variety"
        :form-list="varieties"
        form-check-label="Ajouter un nouveau cépage"
        form-new-data-placeholder="Nom du cépage"
    />
    <select-or-create-form
        :form-data="formData.pruning"
        :form-list="prunings"
        form-check-label="Ajouter un nouveau type de taille"
        form-new-data-placeholder="Nom du type de taille"
    />
    <select-or-create-form
        :form-data="formData.folding"
        :form-list="foldings"
        form-check-label="Ajouter un nouveau type de pliage"
        form-new-data-placeholder="Nom du type de pliage"
    />
    <div class="card mb-3">
        <div class="card-body">
            <h5>Tâches</h5>
            <ul class="list-group mb-2">
                <li class="list-group-item" v-for="task in formData.tasks">
                    <input class="form-check-input me-1" type="checkbox" v-model="task.checked">
                    <label class="form-check-label">{{ task.name }}</label>
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
        {{ invalidDataMessage }}
    </div>
</template>

<script setup>
    import { onMounted, ref, toRaw } from 'vue'

    import SelectOrCreateForm from '../components/select_or_create_form.vue'
    import { send_api } from '../lib/request'

    const props = defineProps([ 'formData', 'invalidData', 'invalidDataMessage' ])
    const varieties = ref([])
    const prunings = ref([])
    const foldings = ref([])
    const new_task_name = ref("")
    const task_name_empty = ref(false)
    const task_name_already_exists = ref(false)

    onMounted(() => {
        // Load varieties
        send_api("GET", "varieties").then((response) => {
            varieties.value = JSON.parse(response.response)
        }).catch((error) => {
            console.error("Error when loading varieties ...")
            console.error(error)
        })
        // Load prunings
        send_api("GET", "prunings").then((response) => {
            prunings.value = JSON.parse(response.response)
        }).catch((error) => {
            console.error("Error when loading prunings ...")
            console.error(error)
        })
        // Load foldings
        send_api("GET", "foldings").then((response) => {
            foldings.value = JSON.parse(response.response)
        }).catch((error) => {
            console.error("Error when loading foldings ...")
            console.error(error)
        })
    })

    const add_task = () => {
        if (new_task_name.value == "") {
            task_name_empty.value = true
            return
        }
        task_name_empty.value = false
        send_api("POST", "tasks", { name: new_task_name.value })
        .then((response) => {
            if (response.status == 400) {
                task_name_already_exists.value = true
            }
            else {
                let task = JSON.parse(response.response)
                task.checked = true
                props.formData.tasks.push(task)
                task_name_already_exists.value = false
                new_task_name.value = ""
            }
            
        })
        .catch((error) => { console.error(error) })
    }

    const create_variety_pruning_folding = () => {
        let properties = [
            { name: "variety", endpoint: "varieties" },
            { name: "pruning", endpoint: "prunings" },
            { name: "folding", endpoint: "foldings" },
        ]
        let post_promises = []
        for (let property of properties) {
            if (props.formData[property.name].id == -1) {
                post_promises.push(new Promise((resolve, reject) => {
                send_api("POST", property.endpoint, { name: props.formData[property.name].name })
                    .then((response) => {
                        resolve(JSON.parse(response.response).id)
                    })
                    .catch((error) => { reject(error) })
                }))
            }
            else {
                post_promises.push(new Promise((resolve) => { resolve(props.formData[property.name].id) }))
            }
        }
        return post_promises
    }

    const check_unique_variety_pruning_folding_name = (out_error) => {
        out_error.message = ""
        if (props.formData.variety.id == -1) {
            for (let variety of toRaw(varieties.value)) {
                if (variety.name == props.formData.variety.name) {
                    out_error.message = "Un cépage avec ce nom existe déjà."
                    return
                }
                    
            }
        }
        if (props.formData.pruning.id == -1) {
            for (let pruning of prunings.value) {
                if (pruning.name == props.formData.pruning.name) {
                    out_error.message = "Une taille avec ce nom existe déjà."
                    return
                }
            }
        }
        if (props.formData.folding.id == -1) {
            for (let folding of foldings.value) {
                if (folding.name == props.formData.folding.name) {
                    out_error.message = "Un pliage avec ce nom existe déjà."
                    return
                }
            }
        }
    }

    defineExpose({
        create_variety_pruning_folding,
        check_unique_variety_pruning_folding_name,
    })
</script>