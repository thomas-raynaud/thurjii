import { createWebHashHistory, createRouter } from 'vue-router'  
import home             from './pages/home.vue'
import plot_creation    from './pages/plot_creation.vue'
import parcelle         from './pages/parcelle.vue'
import map_sandbox      from './pages/map_sandbox.vue'
import about            from './pages/about.vue'

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        {
            path: '/',
            name: 'home',
            component: home
        },
        {
            path: '/map-sandbox',
            name: 'map_sandbox',
            component: map_sandbox
        },
        {
            path: '/creation-parcelle',
            name: 'creation_parcelle',
            component: plot_creation
        },
        {
            path: '/about',
            name: 'about',
            component: about
        },
        {
            path: '/parcelles/:id',
            name: 'parcelle',
            component: parcelle
        }
    ]
})

export default router