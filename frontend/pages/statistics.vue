<template>
    <div class="body row">
        <h2>Statistiques</h2>
        <div>
            <p>Surface totale : {{ total_area }} ha</p>
        </div>
        <div>
            <h3>Progression des tâches</h3>
            <div class="accordion">
                <div v-for="task in tasks" class="accordion-item">
                    <div class="accordion-header">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" :data-bs-target="'#task-panel-' + task.id">
                            <div class="container-fluid">
                            <div class="row align-items-center">
                                <div class="col-2">
                                    <h4>{{ task.name }} ({{ task.area_done }}/{{ task.total_area }}ha)</h4>
                                </div>
                                <div class="col">
                                    <div class="progress">
                                        <div class="progress-bar" :style="'width: ' + task.completion + '%;'" role="progressbar">{{ task.completion }}%</div>
                                    </div>
                                </div>
                            </div>
                            </div>
                        </button>
                    </div>
                    <div :id="'task-panel-' + task.id" class="accordion-collapse collapse">
                        <div class="accordion-body">
                            <div class="row">
                                <div class="col-4">
                                    <h5>Pas commencé</h5>
                                    <ul>
                                        <div v-for="plots_todo_designation in task.plots_todo">
                                            <li>{{ plots_todo_designation.designation }}</li>
                                            <ul>
                                                <li v-for="plot_todo in plots_todo_designation.plots">
                                                    {{ plot_todo.name }}
                                                </li>
                                            </ul>
                                        </div>
                                    </ul>
                                </div>
                                <div class="col-4">
                                    <h5>En cours</h5>
                                    <ul>
                                        <div v-for="plots_in_progress_designation in task.plots_in_progress">
                                            <li>{{ plots_in_progress_designation.designation }}</li>
                                            <ul>
                                                <li v-for="plot_in_progress in plots_in_progress_designation.plots">
                                                    {{ plot_in_progress.name }} ({{ plot_in_progress.completion }}%)
                                                </li>
                                            </ul>
                                        </div>
                                    </ul>
                                </div>
                                <div class="col-4">
                                    <h5>Terminé</h5>
                                    <ul>
                                        <div v-for="plots_done_designation in task.plots_done">
                                            <li>{{ plots_done_designation.designation }}</li>
                                            <ul>
                                                <li v-for="plot_done in plots_done_designation.plots">
                                                    {{ plot_done.name }}
                                                </li>
                                            </ul>
                                        </div>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, onMounted } from 'vue'

    import { settings_store } from '../stores/settings_store'
    import { retrieve_plots, retrieve_tasks } from '../lib/api_retrieval'
    import { send_api } from '../lib/request'

    const total_area = ref(0)
    const tasks = ref([])

    onMounted(() => {
        let get_promises = [
            retrieve_plots(),
            send_api("GET", "designations"),
            retrieve_tasks(),
            send_api("GET", "plot_tasks")
        ]
        Promise.all(get_promises).then((responses) => {
            let plots = responses[0]
            let designations = JSON.parse(responses[1].response)
            let tasks_api = responses[2]
            let plot_tasks = JSON.parse(responses[3].response)
            // Compute total area
            let area = plots.reduce((acc, plot) => { return acc + plot.plot_sections.reduce((acc2, section) => acc2 + section.area, 0) }, 0)
            total_area.value = Math.floor((area / 10000) * 100) / 100
            // Map plot ID to plot index in plots array
            let plot_id_ind_map = new Map()
            for (let i = 0; i < plots.length; i++) {
                plot_id_ind_map.set(plots[i].id, i)
            }
            // Map designation ID to designation index in designations array
            let designation_id_ind_map = new Map()
            for (let i = 0; i < designations.length; i++) {
                designation_id_ind_map.set(designations[i].id, i)
            }
            // Fill tasks
            let task_array = []
            for (let task of tasks_api) {
                if (task.completion == -1) // Ignore tasks that are not linked to any plot (completion = -1)
                    continue
                task.completion = Math.round(task.completion * 10000) / 100
                task.plots_todo = []
                task.plots_in_progress = []
                task.plots_done = []
                task.total_area = 0.0
                task.area_done = 0.0
                let designations_todo_map = new Map()
                let designations_in_progress_map = new Map()
                let designations_done_map = new Map()
                for (let plot_task of plot_tasks) {
                    if (plot_task.season == settings_store.current_season && plot_task.task == task.id) {
                        let plot = plots[plot_id_ind_map.get(plot_task.plot)]
                        let total_area_plot = plot.plot_sections.reduce((acc, section) => acc + section.area, 0)
                        task.area_done += total_area_plot * plot_task.completion
                        task.total_area += total_area_plot
                        let designation = designations[designation_id_ind_map.get(plot.designation)]
                        if (plot_task.completion == 0.0) {
                            fill_plot_table(task.plots_todo, designations_todo_map, plot_task, plot, designation)
                        }
                        else if (plot_task.completion == 100.0) {
                            fill_plot_table(task.plots_done, designations_done_map, plot_task, plot, designation)
                        }
                        else {
                            fill_plot_table(task.plots_in_progress, designations_in_progress_map, plot_task, plot, designation)
                        }
                    }
                }
                task.total_area = Math.floor((task.total_area / 10000) * 100) / 100
                task.area_done = Math.floor((task.area_done / 10000) * 100) / 100
                task_array.push(task)
            }
            tasks.value = task_array
        })
    })

    const fill_plot_table = (plot_table, designations_map, plot_task, plot, designation) => {
        let ind = designations_map.get(designation.id)
        let new_plot = {
            name: plot.name,
            completion: Math.round(plot_task.completion * 10000) / 100
        }
        if (ind == undefined) {
            let designation_ind = plot_table.push({
                designation: designation.name,
                plots: [ new_plot ]
            }) - 1
            designations_map.set(designation.id, designation_ind)
        }
        else {
            plot_table[ind].plots.push(new_plot)
        }
    }
</script>