<template>
  <q-page class="q-pa-md">
    <div class="q-mb-md row items-center">
      <q-btn flat round dense icon="arrow_back" @click="$router.back()" />
      <div class="text-h5 q-ml-md">Избранное</div>
    </div>

    <div v-if="favorites.length === 0" class="text-center q-mt-xl">
      <q-icon name="favorite_border" size="64px" color="grey-5" />
      <div class="text-h6 text-grey-7 q-mt-md">Нет избранных мест</div>
      <div class="text-body2 text-grey-6 q-mt-sm">
        Добавьте автосервисы в избранное для быстрого доступа
      </div>
      <q-btn
        unelevated
        color="primary"
        label="На карту"
        @click="$router.push('/')"
        class="q-mt-md"
      />
    </div>

    <q-list v-else separator>
      <q-item
        v-for="business in favorites"
        :key="business.id"
        clickable
        @click="openBusiness(business)"
      >
        <q-item-section avatar>
          <q-avatar :color="statusColor(business.status)" text-color="white">
            <q-icon name="local_car_wash" />
          </q-avatar>
        </q-item-section>

        <q-item-section>
          <q-item-label>{{ business.name }}</q-item-label>
          <q-item-label caption>{{ business.address }}</q-item-label>
          <q-item-label caption class="q-mt-xs">
            <q-chip :color="statusColor(business.status)" text-color="white" size="sm">
              {{ statusLabel(business.status) }}
            </q-chip>
          </q-item-label>
        </q-item-section>

        <q-item-section side>
          <q-btn
            flat
            round
            dense
            icon="favorite"
            color="red"
            @click.stop="removeFromFavorites(business.id)"
          />
        </q-item-section>
      </q-item>
    </q-list>
  </q-page>
</template>

<script>
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'

export default defineComponent({
  name: 'FavoritesPage',

  setup() {
    const router = useRouter()
    const favorites = ref([])

    const statusLabel = (status) => {
      const labels = {
        available: 'Свободно',
        busy: 'Занято',
        very_busy: 'Очень загружены'
      }
      return labels[status] || status
    }

    const statusColor = (status) => {
      const colors = {
        available: 'green',
        busy: 'orange',
        very_busy: 'red'
      }
      return colors[status] || 'grey'
    }

    const openBusiness = (business) => {
      router.push({ name: 'map', query: { businessId: business.id } })
    }

    const removeFromFavorites = (id) => {
      // TODO: Реализовать удаление из избранного
      console.log('Remove from favorites:', id)
    }

    return {
      favorites,
      statusLabel,
      statusColor,
      openBusiness,
      removeFromFavorites
    }
  }
})
</script>
