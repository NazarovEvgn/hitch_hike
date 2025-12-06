<template>
  <q-page class="q-pa-md">
    <div class="row">
      <div class="col-12">
        <div class="text-h5 q-mb-md">Настройки</div>

        <!-- Main card with tabs -->
        <q-card flat bordered class="profile-card">
          <q-tabs
            v-model="tab"
            dense
            class="text-grey-7"
            active-color="primary"
            indicator-color="primary"
            align="left"
            narrow-indicator
          >
            <q-tab name="profile" label="Профиль" />
            <q-tab name="hours" label="Часы работы" />
            <q-tab name="photos" label="Фотографии" />
          </q-tabs>

          <q-separator />

          <q-tab-panels v-model="tab" animated>
            <!-- Profile Tab -->
            <q-tab-panel name="profile" class="q-pa-md">
              <q-form @submit="saveProfile" class="profile-form">
                <div class="row q-col-gutter-md">
                  <div class="col-12 col-md-6">
                    <q-input
                      v-model="businessForm.name"
                      label="Название *"
                      filled
                      dense
                      :rules="[val => !!val || 'Обязательное поле']"
                    />
                  </div>

                  <div class="col-12 col-md-6">
                    <q-select
                      v-model="businessForm.type"
                      :options="businessTypes"
                      option-value="value"
                      option-label="label"
                      emit-value
                      map-options
                      label="Тип бизнеса *"
                      filled
                      dense
                      :rules="[val => !!val || 'Обязательное поле']"
                    />
                  </div>

                  <div class="col-12">
                    <q-input
                      v-model="businessForm.address"
                      label="Адрес *"
                      filled
                      dense
                      :rules="[val => !!val || 'Обязательное поле']"
                    />
                  </div>

                  <div class="col-12 col-md-6">
                    <q-input
                      v-model="businessForm.phone"
                      label="Телефон *"
                      filled
                      dense
                      mask="+7 (###) ###-##-##"
                      :rules="[val => !!val || 'Обязательное поле']"
                    />
                  </div>

                  <div class="col-12 col-md-6">
                    <q-input
                      v-model="businessForm.email"
                      label="Email"
                      filled
                      dense
                      type="email"
                    />
                  </div>

                  <div class="col-12">
                    <q-input
                      v-model="businessForm.description"
                      label="Описание"
                      filled
                      dense
                      type="textarea"
                      rows="3"
                      autogrow
                    />
                  </div>

                  <div class="col-12 col-md-6">
                    <q-input
                      v-model="businessForm.logo_url"
                      label="URL логотипа"
                      filled
                      dense
                    />
                  </div>

                  <div v-if="businessForm.logo_url" class="col-12 col-md-6 flex items-center">
                    <q-img
                      :src="businessForm.logo_url"
                      style="max-width: 80px; max-height: 80px; border-radius: 4px;"
                      fit="contain"
                      @error="() => $q.notify({ type: 'warning', message: 'Ошибка загрузки изображения' })"
                    />
                  </div>

                  <div class="col-12 col-md-6">
                    <q-input
                      v-model="businessForm.lat"
                      label="Широта"
                      filled
                      dense
                      readonly
                    />
                  </div>

                  <div class="col-12 col-md-6">
                    <q-input
                      v-model="businessForm.lon"
                      label="Долгота"
                      filled
                      dense
                      readonly
                    />
                  </div>
                </div>

                <div class="row q-mt-md">
                  <q-btn
                    label="Сохранить"
                    type="submit"
                    color="primary"
                    unelevated
                    :loading="loadingSaveProfile"
                    :disable="loadingSaveProfile"
                    class="q-px-lg"
                  />
                </div>
              </q-form>
            </q-tab-panel>

            <!-- Business Hours Tab -->
            <q-tab-panel name="hours" class="q-pa-md">
              <q-form @submit="saveBusinessHours">
                <div class="business-hours-table">
                  <div v-for="(day, index) in businessHours" :key="index" class="hours-row">
                    <div class="day-name">{{ getDayName(index) }}</div>

                    <q-checkbox
                      v-model="day.is_closed"
                      label="Выходной"
                      dense
                      @update:model-value="toggleDayClosed(index)"
                      class="closed-checkbox"
                    />

                    <q-input
                      v-model="day.open_time"
                      label="Открытие"
                      filled
                      dense
                      mask="##:##"
                      :disable="day.is_closed"
                      placeholder="09:00"
                      class="time-input"
                    >
                      <template v-slot:append>
                        <q-icon name="schedule" size="xs" />
                      </template>
                    </q-input>

                    <span class="time-separator">—</span>

                    <q-input
                      v-model="day.close_time"
                      label="Закрытие"
                      filled
                      dense
                      mask="##:##"
                      :disable="day.is_closed"
                      placeholder="18:00"
                      class="time-input"
                    >
                      <template v-slot:append>
                        <q-icon name="schedule" size="xs" />
                      </template>
                    </q-input>
                  </div>
                </div>

                <div class="row q-mt-md">
                  <q-btn
                    label="Сохранить"
                    type="submit"
                    color="primary"
                    unelevated
                    :loading="loadingSaveHours"
                    :disable="loadingSaveHours"
                    class="q-px-lg"
                  />
                </div>
              </q-form>
            </q-tab-panel>

            <!-- Photos Tab -->
            <q-tab-panel name="photos" class="q-pa-md">
              <!-- Add photo section -->
              <div class="add-photo-section q-mb-lg">
                <div class="text-subtitle2 q-mb-sm">Добавить фотографию</div>
                <div class="row q-col-gutter-sm">
                  <div class="col-12 col-md-8">
                    <q-input
                      v-model="newPhotoUrl"
                      label="URL фотографии"
                      filled
                      dense
                      placeholder="https://example.com/photo.jpg"
                    />
                  </div>
                  <div class="col-12 col-md-4">
                    <q-btn
                      label="Добавить"
                      color="primary"
                      unelevated
                      :loading="loadingAddPhoto"
                      :disable="!newPhotoUrl || loadingAddPhoto"
                      @click="addPhoto"
                      class="full-width"
                    />
                  </div>
                </div>
              </div>

              <q-separator class="q-mb-md" />

              <!-- Photos grid -->
              <div v-if="photos.length > 0" class="photos-grid">
                <div
                  v-for="photo in photos"
                  :key="photo.id"
                  class="photo-item"
                >
                  <div class="photo-wrapper">
                    <q-img
                      :src="photo.photo_url"
                      :ratio="1"
                      fit="cover"
                      @error="() => $q.notify({ type: 'warning', message: 'Ошибка загрузки' })"
                    >
                      <div v-if="photo.is_main" class="photo-badge">
                        <q-badge color="positive" label="Главное" />
                      </div>
                    </q-img>
                  </div>

                  <div class="photo-actions">
                    <q-btn
                      v-if="!photo.is_main"
                      label="Сделать главным"
                      size="sm"
                      color="primary"
                      flat
                      dense
                      :loading="loadingSetMain === photo.id"
                      @click="setMainPhoto(photo.id)"
                      class="full-width"
                    />
                    <q-btn
                      v-else
                      label="Главное фото"
                      size="sm"
                      color="positive"
                      flat
                      dense
                      disable
                      class="full-width"
                    />
                    <q-btn
                      icon="delete"
                      size="sm"
                      color="negative"
                      flat
                      dense
                      :loading="loadingDeletePhoto === photo.id"
                      @click="confirmDeletePhoto(photo.id)"
                    />
                  </div>
                </div>
              </div>

              <div v-else class="empty-state">
                <q-icon name="photo_library" size="64px" color="grey-4" />
                <div class="text-grey-6 q-mt-sm">Фотографии не добавлены</div>
              </div>
            </q-tab-panel>
          </q-tab-panels>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import { api } from 'boot/axios'

export default defineComponent({
  name: 'ProfilePage',

  setup() {
    const $q = useQuasar()
    const tab = ref('profile')

    const businessTypes = [
      { value: 'car_wash', label: 'Автомойка' },
      { value: 'repair_shop', label: 'Автосервис / Ремонт' },
      { value: 'tire_service', label: 'Шиномонтаж' },
      { value: 'beauty_salon', label: 'Салон красоты' }
    ]

    const businessForm = ref({
      name: '',
      type: '',
      address: '',
      phone: '',
      email: '',
      description: '',
      logo_url: '',
      lat: null,
      lon: null
    })

    const businessHours = ref([
      { day_of_week: 0, open_time: null, close_time: null, is_closed: true },
      { day_of_week: 1, open_time: null, close_time: null, is_closed: true },
      { day_of_week: 2, open_time: null, close_time: null, is_closed: true },
      { day_of_week: 3, open_time: null, close_time: null, is_closed: true },
      { day_of_week: 4, open_time: null, close_time: null, is_closed: true },
      { day_of_week: 5, open_time: null, close_time: null, is_closed: true },
      { day_of_week: 6, open_time: null, close_time: null, is_closed: true }
    ])

    const photos = ref([])
    const newPhotoUrl = ref('')

    const loadingSaveProfile = ref(false)
    const loadingSaveHours = ref(false)
    const loadingAddPhoto = ref(false)
    const loadingSetMain = ref(null)
    const loadingDeletePhoto = ref(null)

    const getDayName = (dayIndex) => {
      const days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
      return days[dayIndex]
    }

    const toggleDayClosed = (index) => {
      if (businessHours.value[index].is_closed) {
        businessHours.value[index].open_time = null
        businessHours.value[index].close_time = null
      }
    }

    const loadBusinessProfile = async () => {
      try {
        const response = await api.get('/admin/business/profile')
        businessForm.value = {
          name: response.data.name,
          type: response.data.type,
          address: response.data.address,
          phone: response.data.phone,
          email: response.data.email || '',
          description: response.data.description || '',
          logo_url: response.data.logo_url || '',
          lat: response.data.lat,
          lon: response.data.lon
        }
      } catch (error) {
        console.error('Error loading business profile:', error)
        $q.notify({
          type: 'negative',
          message: 'Ошибка загрузки профиля',
          caption: error.response?.data?.detail || error.message
        })
      }
    }

    const loadBusinessHours = async () => {
      try {
        const response = await api.get('/admin/business-hours')
        if (response.data && response.data.length === 7) {
          businessHours.value = response.data.map(hour => ({
            day_of_week: hour.day_of_week,
            open_time: hour.open_time || null,
            close_time: hour.close_time || null,
            is_closed: hour.is_closed
          }))
        }
      } catch (error) {
        console.error('Error loading business hours:', error)
        $q.notify({
          type: 'negative',
          message: 'Ошибка загрузки времени работы',
          caption: error.response?.data?.detail || error.message
        })
      }
    }

    const saveProfile = async () => {
      loadingSaveProfile.value = true
      try {
        await api.patch('/admin/business/profile', {
          name: businessForm.value.name,
          address: businessForm.value.address,
          phone: businessForm.value.phone,
          email: businessForm.value.email || null,
          description: businessForm.value.description || null,
          logo_url: businessForm.value.logo_url || null
        })
        $q.notify({
          type: 'positive',
          message: 'Профиль успешно обновлен',
          icon: 'check_circle'
        })
      } catch (error) {
        console.error('Error saving profile:', error)
        $q.notify({
          type: 'negative',
          message: 'Ошибка сохранения профиля',
          caption: error.response?.data?.detail || error.message
        })
      } finally {
        loadingSaveProfile.value = false
      }
    }

    const saveBusinessHours = async () => {
      loadingSaveHours.value = true
      try {
        const hoursData = businessHours.value.map(hour => ({
          day_of_week: hour.day_of_week,
          open_time: hour.is_closed ? null : hour.open_time,
          close_time: hour.is_closed ? null : hour.close_time,
          is_closed: hour.is_closed
        }))

        await api.put('/admin/business-hours', {
          hours: hoursData
        })

        $q.notify({
          type: 'positive',
          message: 'Время работы успешно обновлено',
          icon: 'check_circle'
        })
      } catch (error) {
        console.error('Error saving business hours:', error)
        $q.notify({
          type: 'negative',
          message: 'Ошибка сохранения времени работы',
          caption: error.response?.data?.detail || error.message
        })
      } finally {
        loadingSaveHours.value = false
      }
    }

    const loadPhotos = async () => {
      try {
        const response = await api.get('/admin/business/photos')
        photos.value = response.data.sort((a, b) => {
          if (a.is_main) return -1
          if (b.is_main) return 1
          return a.display_order - b.display_order
        })
      } catch (error) {
        console.error('Error loading photos:', error)
        $q.notify({
          type: 'negative',
          message: 'Ошибка загрузки фотографий',
          caption: error.response?.data?.detail || error.message
        })
      }
    }

    const addPhoto = async () => {
      if (!newPhotoUrl.value) return

      loadingAddPhoto.value = true
      try {
        await api.post('/admin/business/photos', {
          photo_url: newPhotoUrl.value,
          display_order: photos.value.length
        })

        $q.notify({
          type: 'positive',
          message: 'Фотография добавлена',
          icon: 'check_circle'
        })

        newPhotoUrl.value = ''
        await loadPhotos()
      } catch (error) {
        console.error('Error adding photo:', error)
        $q.notify({
          type: 'negative',
          message: 'Ошибка добавления фотографии',
          caption: error.response?.data?.detail || error.message
        })
      } finally {
        loadingAddPhoto.value = false
      }
    }

    const setMainPhoto = async (photoId) => {
      loadingSetMain.value = photoId
      try {
        await api.patch(`/admin/business/photos/${photoId}/set-main`)

        $q.notify({
          type: 'positive',
          message: 'Главное фото обновлено',
          icon: 'check_circle'
        })

        await loadPhotos()
      } catch (error) {
        console.error('Error setting main photo:', error)
        $q.notify({
          type: 'negative',
          message: 'Ошибка установки главного фото',
          caption: error.response?.data?.detail || error.message
        })
      } finally {
        loadingSetMain.value = null
      }
    }

    const confirmDeletePhoto = (photoId) => {
      $q.dialog({
        title: 'Подтверждение',
        message: 'Вы уверены, что хотите удалить это фото?',
        cancel: {
          label: 'Отмена',
          flat: true
        },
        ok: {
          label: 'Удалить',
          color: 'negative'
        },
        persistent: true
      }).onOk(() => {
        deletePhoto(photoId)
      })
    }

    const deletePhoto = async (photoId) => {
      loadingDeletePhoto.value = photoId
      try {
        await api.delete(`/admin/business/photos/${photoId}`)

        $q.notify({
          type: 'positive',
          message: 'Фотография удалена',
          icon: 'check_circle'
        })

        await loadPhotos()
      } catch (error) {
        console.error('Error deleting photo:', error)
        $q.notify({
          type: 'negative',
          message: 'Ошибка удаления фотографии',
          caption: error.response?.data?.detail || error.message
        })
      } finally {
        loadingDeletePhoto.value = null
      }
    }

    onMounted(() => {
      loadBusinessProfile()
      loadBusinessHours()
      loadPhotos()
    })

    return {
      tab,
      businessTypes,
      businessForm,
      businessHours,
      photos,
      newPhotoUrl,
      loadingSaveProfile,
      loadingSaveHours,
      loadingAddPhoto,
      loadingSetMain,
      loadingDeletePhoto,
      getDayName,
      toggleDayClosed,
      saveProfile,
      saveBusinessHours,
      addPhoto,
      setMainPhoto,
      confirmDeletePhoto
    }
  }
})
</script>

<style scoped>
.profile-card {
  background: white;
  border-radius: 8px;
}

.profile-form {
  max-width: 900px;
}

/* Business Hours Table */
.business-hours-table {
  max-width: 900px;
}

.hours-row {
  display: grid;
  grid-template-columns: 140px 120px 1fr 30px 1fr;
  gap: 12px;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.hours-row:last-child {
  border-bottom: none;
}

.day-name {
  font-weight: 500;
  color: #333;
}

.closed-checkbox {
  font-size: 14px;
}

.time-input {
  max-width: 160px;
}

.time-separator {
  color: #999;
  font-size: 14px;
  text-align: center;
}

/* Photos Grid */
.photos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.photo-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  background: white;
}

.photo-wrapper {
  position: relative;
}

.photo-badge {
  position: absolute;
  top: 8px;
  right: 8px;
}

.photo-actions {
  padding: 8px;
  display: flex;
  gap: 4px;
  align-items: center;
  justify-content: space-between;
  background: #fafafa;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

/* Responsive */
@media (max-width: 768px) {
  .hours-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .time-separator {
    display: none;
  }

  .photos-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>
