<template>
  <div class="fullscreen bg-grey-2 text-center q-pa-md flex flex-center">
    <div>
      <div style="font-size: 30vh" class="text-grey-5">
        404
      </div>

      <div class="text-h2 text-grey-7" style="opacity:.4">
        Страница не найдена
      </div>

      <q-btn
        class="q-mt-xl"
        color="primary"
        label="На главную"
        unelevated
        to="/"
        size="lg"
      />
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'ErrorNotFound'
})
</script>
