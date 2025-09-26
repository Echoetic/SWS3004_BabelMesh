import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/DashboardFixed.vue'
import Settings from '../views/Settings.vue'
import IPDetection from '../views/IPDetection.vue'
import PodMonitor from '../views/PodMonitor.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  },
  {
    path: '/ip-detection',
    name: 'IPDetection',
    component: IPDetection,
    meta: { title: 'IP检测' }
  },
  {
    path: '/pod-monitor',
    name: 'PodMonitor',
    component: PodMonitor,
    meta: { title: 'Pod监控' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
