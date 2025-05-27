import { createWebHashHistory, createRouter } from 'vue-router'  
import home             from './pages/home.vue'
import map_page         from './pages/map.vue'
import statistics       from './pages/statistics.vue'
import about            from './pages/about.vue'
import plot_creation    from './pages/plot_creation.vue'
import plot             from './pages/plot.vue'
import logs             from './pages/logs.vue'
import log_creation     from './pages/log_creation.vue'

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        {
            path: '/',
            name: 'home',
            component: home
        },
        {
            path: '/logs',
            name: 'logs',
            component: logs
        },
        {
            path: '/map',
            name: 'map',
            component: map_page
        },
        {
            path: '/statistics',
            name: 'statistics',
            component: statistics
        },
        {
            path: '/about',
            name: 'about',
            component: about
        },
        {
            path: '/plot-creation',
            name: 'plot_creation',
            component: plot_creation
        },
        {
            path: '/log-creation',
            name: 'log_creation',
            component: log_creation
        },
        {
            path: '/plots/:id',
            name: 'plot',
            component: plot
        }
    ]
})

export default router