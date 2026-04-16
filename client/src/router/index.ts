import { createRouter, createWebHistory } from 'vue-router'
import CodeReview from '../views/CodeReview.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'code-review',
      component: CodeReview
    },
    {
      path: '/review',
      name: 'review',
      component: CodeReview
    }
  ]
})

export default router
