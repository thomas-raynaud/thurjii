import { createWebHashHistory, createRouter } from 'vue-router'  
import home                     from './components/home.vue'
import map_canvas                     from './components/map.vue'
import planning                 from './components/planning.vue'
import about                 from './components/about.vue'

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        {
            path: '/',
            name: 'home',
            component: home
        },
        {
            path: '/map',
            name: 'map_canvas',
            component: map_canvas
        },
        {
            path: '/planning',
            name: 'planning',
            component: planning
        },
        {
            path: '/about',
            name: 'about',
            component: about
        }
    ]
})

export default router


