<template>
    <div class="row mb-3 align-items-center">
        <div class="col">
            <select class="form-control" v-model="props.formData.id" :disabled="new_data">
                <option v-for="form_option in props.formList" :value="form_option.id">{{ form_option.name }}</option>
            </select>
        </div>
        <div class="col form-check">
            <input type="checkbox" class="form-check-input" v-model="new_data" :disabled="props.formList.length == 0">
            <label class="form-check-label">{{ props.formCheckLabel }}</label>
        </div>
        <div class="col">
            <input class="form-control" v-model="new_name" :disabled="!new_data" :placeholder="props.formNewDataPlaceholder">
        </div>
    </div>
</template>

<script setup>
    import { ref, watch, onMounted } from 'vue'

    const props = defineProps([ 'formData', 'formList', 'formCheckLabel', 'formNewDataPlaceholder' ])
    const new_data = ref(false)
    const new_name = ref("")

    onMounted(() => {
        if (props.formList.length == 0)
            new_data.value = true
        else {
            props.formData.id = props.formList[0].id
            props.formData.name = props.formList[0].name
        }
    })

    watch(new_data, (new_val) => {
        if (new_val) {
            props.formData.id = -1
        }
        else {
            props.formData.id = props.formList[0].id
        }
    })

    watch(() => props.formList.length, (nb_elements) => {
        if (nb_elements > 0) {
            new_data.value = false
            props.formData.id = props.formList[0].id
            props.formData.name = props.formList[0].name
        }
    })

    watch(new_name, (new_val) => {
        if (new_data.value)
            props.formData.name = new_val
    })

    watch(() => props.formData.id, (new_id) => {
        if (new_id != -1) {
            for (let form_option of props.formList) {
                if (form_option.id == new_id) {
                    props.formData.name = form_option.name
                    break
                }
            }
        }
    })
</script>