import { createWebHashHistory, createRouter } from 'vue-router'  
import home                     from './components/home.vue'
import planning                 from './components/planning.vue'

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        {
            path: '/',
            name: 'home',
            component: home
        },
        {
            path: '/planning',
            name: 'planning',
            component: planning
        }
    ]
})

export default router


