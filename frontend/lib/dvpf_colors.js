import { map_store } from '../stores/map_store'
import { settings_store } from '../stores/settings_store'
import { DVPF_NAMES } from './const'
import { send_api } from './request'

const fill_regions_dvpf = (plots) => {
    let regions_dvpf = {
        designation: [],
        variety: [],
        pruning: [],
        folding: [],
    }
    for (let plot of plots) {
        for (let i = 0; i < plot.plot_sections.length; i++) {
            regions_dvpf.designation.push(plot.designation)
            regions_dvpf.variety.push(plot.variety)
            regions_dvpf.pruning.push(plot.pruning)
            regions_dvpf.folding.push(plot.folding)
        }
    }
    return regions_dvpf
}

const load_dvpf_map = () => {
    let dvpf_map = {
        designation: new Map(),
        variety: new Map(),
        pruning: new Map(),
        folding: new Map(),
    }
    return new Promise((resolve) => {
        let get_promises = [
            new Promise((resolve) => {
                send_api("GET", "designations").then((response) => {
                    let designations = JSON.parse(response.response)
                    for (let designation of designations) {
                        dvpf_map.designation.set(designation.id, designation)
                    }
                    resolve()
                })
            }),
            new Promise((resolve) => {
                send_api("GET", "varieties").then((response) => {
                    let varieties = JSON.parse(response.response)
                    for (let variety of varieties) {
                        dvpf_map.variety.set(variety.id, variety)
                    }
                    resolve()
                })
            }),
            new Promise((resolve) => {
                send_api("GET", "prunings").then((response) => {
                    let prunings = JSON.parse(response.response)
                    for (let pruning of prunings) {
                        dvpf_map.pruning.set(pruning.id, pruning)
                    }
                    resolve()
                })
            }),
            new Promise((resolve) => {
                send_api("GET", "foldings").then((response) => {
                    let foldings = JSON.parse(response.response)
                    for (let folding of foldings) {
                        dvpf_map.folding.set(folding.id, folding)
                    }
                    resolve()
                })
            }),
        ]
        Promise.all(get_promises).then(() => {
            resolve(dvpf_map)
        })
    })
}

const set_colors = (dvpf_map, regions_dvpf) => {
    let color_prop = DVPF_NAMES[settings_store.plot_color_type]
    map_store.regions_color = new Array(map_store.regions.length)
    for (let i = 0; i < map_store.regions.length; i++) {
        let prop_ind = regions_dvpf[color_prop][i]
        let color = dvpf_map[color_prop].get(prop_ind).color
        map_store.regions_color[i] = color
    }
}

export {
    fill_regions_dvpf,
    load_dvpf_map,
    set_colors
}