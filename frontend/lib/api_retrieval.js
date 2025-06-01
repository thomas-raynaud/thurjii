import { send_api } from './request'

const format_plot = (plot_api) => {
    return {
        id: plot_api.id,
        name: plot_api.properties.name,
        variety: plot_api.properties.variety,
        pruning: plot_api.properties.pruning,
        folding: plot_api.properties.folding,
        area: plot_api.properties.area,
        region: plot_api.geometry.coordinates[0].map((x) => { return { x: x[0], y: x[1] }}),
    }
}

const retrieve_plots = () => {
    return new Promise((resolve, reject) => {
        send_api("GET", "plots").then((response) => {
            if (response.status == 400) {
                console.error("Error when loading plots ...")
                reject(JSON.parse(response.response))
            }
            else {
                let plots_api = JSON.parse(response.response).features
                let plots = []
                for (let plot_api of plots_api) {
                    plots.push(format_plot(plot_api))
                }
                resolve(plots)
            }
            
        }).catch((error) => {
            console.error("Error when loading plots ...")
            console.error(error)
            reject(error)
        })
    })
}

const retrieve_plot = (plot_id) => {
    return new Promise((resolve, reject) => {
        send_api("GET", "plots/" + plot_id).then((response) => {
            if (response.status == 400) {
                console.error("Error when loading plots ...")
                reject(JSON.parse(response.response))
            }
            else {
                let plot_api = JSON.parse(response.response)
                resolve(format_plot(plot_api))
            }
        }).catch((error) => {
            console.error("Error when loading plots ...")
            console.error(error)
            reject(error)
        })
    })
}

const retrieve_tasks = () => {
    return new Promise((resolve, reject) => {
        send_api("GET", "tasks").then((response) => {
            resolve(JSON.parse(response.response))
        }).catch((error) => {
            console.error("Error when loading tasks ...")
            console.error(error)
            reject(error)
        })
    })
}

const retrieve_plot_season_plot_tasks = (plot_id, year) => {
    return new Promise((resolve, reject) => {
        send_api("GET", "plots/" + plot_id + "/plot_tasks/" + year).then((response) => {
            if (response.status == 404) {
                reject({
                    status: 404, 
                    message: "Error: tasks not found for plot " + plot_id + " - season " + year
                })
            }
            else {
                resolve(JSON.parse(response.response))
            }
        })
    })
}

const retrieve_logs = (year) => {
    return new Promise((resolve, reject) => {
        send_api("GET", "logs/season/" + year).then((response) => {
            if (response.status == 404) {
                console.error("Error when loading logs ...")
                let error = JSON.parse(response.response)
                console.error(error)
                reject(error)
            }
            resolve(JSON.parse(response.response))
        }).catch((error) => {
            console.error("Error when loading logs ...")
            console.error(error)
            reject(error)
        })
    })
}

const retrieve_plot_lines = (plot_id) => {
    return new Promise((resolve, reject) => {
        send_api("GET", "plots/" + plot_id + "/lines").then((response) => {
            let lines_api = JSON.parse(response.response).features
            let lines = []
            for (let i = 0; i < lines_api.length; i++) {
                lines.push({
                    start: {
                        x: lines_api[i].geometry.coordinates[0][0],
                        y: lines_api[i].geometry.coordinates[0][1],
                    },
                    end: {
                        x: lines_api[i].geometry.coordinates[1][0],
                        y: lines_api[i].geometry.coordinates[1][1],
                    },
                    id: lines_api[i].id
                })
            }
            resolve(lines)
        }).catch((error) => {
            console.error("Error when loading lines of plot #" + plot_id + " ...")
            console.error(error)
            reject(error)
        })
    })
}

const retrieve_plot_line_states = (plot_id, year) => {
    return new Promise((resolve) => {
        send_api("GET", "plots/" + plot_id + "/lines/" + year + "/state").then((response) => {
            resolve(JSON.parse(response.response))
        })
    })
}

const get_current_season = () => {
    return new Promise((resolve) => {
        send_api("GET", "seasons").then((response) => {
            let seasons = JSON.parse(response.response)
            if (seasons.length == 0 || seasons[0].end !== null) {
                // Create a new season
                let date = new Date()
                let year = date.getFullYear()
                let month = date.getMonth() + 1
                if (month > 8) // If in september or after, we start the season of the following year
                    year += 1
                month = (month < 10 ? "0" + month : "" + month)
                let day = date.getDate()
                day = (day < 10 ? "0" + day : "" + day)
                let beginning_season = year + "-" + month + "-" + day
                send_api("POST", "seasons", { year : "" + year, start: beginning_season })
                .then((response) => {
                    resolve(JSON.parse(response.response).year)
                })
            }
            else {
                resolve(seasons[0].year)
            }
        })
    })
}

export {
    retrieve_plots,
    retrieve_plot,
    retrieve_tasks,
    retrieve_plot_season_plot_tasks,
    retrieve_logs,
    retrieve_plot_lines,
    retrieve_plot_line_states,
    get_current_season,
}