import { reactive } from 'vue'
import { compute_bb, get_polygon_center } from '../lib/geometry'
import { send_api } from '../lib/request'

export const data_store = reactive({
    season: null,
    parcelles_bb: [ [ -1, -1 ], [ -1, -1] ],
    parcelles_regions: [],
    parcelles_regions_names: [],
    parcelles_regions_centers: [],
    parcelles_regions_ids: [],
    compute_parcelles_bb() {
        return new Promise((resolve) => {
            if (this.parcelles_regions == 0) {
                send_api("GET", "parcelles").then((response) => {
                    let parcelles_api = JSON.parse(response.response).features
                    this.parcelles_regions = []
                    parcelles_api.forEach(parcelle_api => {
                        let region = parcelle_api.geometry.coordinates[0].map((x) => { return { x: x[0], y: x[1] }})
                        this.parcelles_regions.push(region)
                        this.parcelles_regions_names.push(parcelle_api.properties.nom)
                        this.parcelles_regions_centers.push(get_polygon_center(region))
                        this.parcelles_regions_ids.push(parcelle_api.id)
                    })
                    let points = [].concat(...this.parcelles_regions)
                    this.parcelles_bb = compute_bb(points)
                    resolve()
                })
            }
            else {
                let points = [].concat(...this.parcelles_regions)
                this.parcelles_bb = compute_bb(points)
                resolve()
            }
        })
    }
})