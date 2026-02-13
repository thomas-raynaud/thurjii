<template>
    <div class="body row">
        <div class="col">
            <div class="card">
                <div class="card-body">
                    <div class="row align-items-center mb-3">
                        <div class="col-md-auto">
                            <h3>Logs</h3>
                        </div>
                        <div class="col">
                            <button
                                type="button" class="btn btn-light"
                                @click="$router.push('log-creation')"
                            >
                                Ajouter un log
                            </button>
                        </div>
                    </div>
                    <div>
                        <div class="col mb-3"
                            v-for="log in logs"
                            :key="log.id"
                        >
                            <div class="card">
                                <div class="card-body">
                                    <div class="row">
                                        <div class="col">
                                            <h5 class="card-title">{{ log.plot_name + " - " + log.task_name }}</h5>
                                        </div>
                                        <div class="col-auto">
                                            <button
                                                type="button" class="btn btn-outline-danger"
                                                @click="delete_log(log.id)"
                                            >
                                                Supprimer
                                            </button>
                                        </div>
                                    </div>
                                    <h6 class="card-subtitle mb-2 text-body-secondary">{{ log.date }}</h6>
                                    <p class="card-text"> Temps passé : {{ log.nb_hours }} </p>
                                    <p class="card-text"> {{ log.comment }} </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <toast ref="toast_component" />
</template>

<style scoped>
</style>

<script setup>
    import { ref, onMounted, useTemplateRef } from 'vue'

    import Toast from '../components/toast.vue'

    import {
        retrieve_logs,
        get_current_season
    } from '../lib/api_retrieval'
    import { settings_store } from '../stores/settings_store'
    import { send_api } from '../lib/request'

    const logs = ref([])
    const toast_component = useTemplateRef("toast_component")

    onMounted(() => {
        get_current_season().then((current_season) => {
            settings_store.current_season = current_season
            load_logs()
        })
        
    })

    const load_logs = () => {
        retrieve_logs(settings_store.current_season).then((in_logs) => {
            logs.value = in_logs
            for (let i = 0; i < logs.value.length; i++) {
                let nb_hours = parseFloat(logs.value[i].nb_hours)
                let nb_hours_int = Math.floor(nb_hours)
                let nb_minutes = (nb_hours - nb_hours_int) * 60
                logs.value[i].nb_hours = nb_hours_int + "h" + ((nb_minutes > 0) ? nb_minutes : "")
            }
        })
        .catch(() => {})
    }

    const delete_log = (log_id) => {
        send_api("DELETE", "logs/" + log_id).then((response) => {
            if (response.status == 500) {
                console.error("Could not delete log #" + log_id + " ...")
                toast_component.value.display_toast("Erreur : le log n'a pas pu être supprimé ...")
            }
            else {
                load_logs()
                toast_component.value.display_toast("Log supprimé")
            }
        }).catch((error) => {
            console.error("Could not delete plot #" + plot.value.id + " ...")
            console.error(error)
            toast_component.value.display_toast("Erreur : le log n'a pas pu être supprimé ...")
        })
    }
</script>