import { reactive } from 'vue'
import { compute_bb } from '../lib/geometry'
import { send_api } from '../lib/request'

export const data_store = reactive({
    season: null,
    parcelles_bb: [ [ -1, -1 ], [ -1, -1] ],
    compute_parcelles_bb() {
        return new Promise((resolve) => {
            send_api("GET", "parcelles").then((response) => {
                let parcelles_api = JSON.parse(response.response).features
                let parcelles_regions = []
                parcelles_api.forEach(parcelle_api => {
                    parcelles_regions.push(parcelle_api.geometry.coordinates[0].map((x) => { return { x: x[0], y: x[1] }}))
                })
                let points = [].concat(...parcelles_regions)
                this.parcelles_bb = compute_bb(points)
                resolve()
            })
        })
    }
})