<template>
    <div class="body row">
        <h2>Logs</h2>
        <div>
            <button
                type="button" class="btn btn-light"
                @click="$router.push('creation-log')"
            >
                Ajouter un log
            </button>
        </div>
    </div>
</template>

<style scoped>
</style>

<script setup>
    import { ref, onMounted } from 'vue'

    import { send_api } from '../lib/request'

    const logs = ref([])

    onMounted(() => {
        load_logs()
    })

    const load_logs = () => {
        send_api("GET", "logs").then((response) => {

        }).catch((error) => {
            console.error("Error when loading logs ...")
            console.error(error)
        })
    }
</script>