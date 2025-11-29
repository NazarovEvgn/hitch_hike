<template>
  <q-page class="flex flex-center">
    <div class="text-center">
      <div class="text-h1 text-grey-5">404</div>
      <div class="text-h5 q-mb-md">Страница не найдена</div>
      <q-btn color="primary" label="На главную" :to="{ name: 'home' }" />
    </div>
  </q-page>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'ErrorNotFound'
})
</script>
