/* eslint-env node */

const { configure } = require('quasar/wrappers');

module.exports = configure(function (ctx) {
  return {
    eslint: {
      warnings: true,
      errors: true
    },

    boot: [
      'axios',
    ],

    css: [
      'app.scss'
    ],

    sassVariables: 'src/css/quasar.variables.scss',

    extras: [
      'roboto-font',
      'material-icons',
    ],

    build: {
      target: {
        browser: ['es2019', 'edge88', 'firefox78', 'chrome87', 'safari13.1'],
        node: 'node20'
      },

      vueRouterMode: 'history',

      env: {
        API_URL: process.env.API_URL || 'http://127.0.0.1:8000/api/v1',
        DGIS_API_KEY: 'bc1703bf-053c-4f08-abed-a8817260c0e7'
      }
    },

    devServer: {
      open: true,
      port: 9000
    },

    framework: {
      config: {},

      plugins: [
        'Notify',
        'Dialog',
        'Loading',
        'LocalStorage'
      ]
    },

    animations: [],

    ssr: {
      pwa: false,
      prodPort: 3000,
      middlewares: [
        'render'
      ]
    },

    pwa: {
      workboxMode: 'GenerateSW',
      injectPwaMetaTags: true,
      swFilename: 'sw.js',
      manifestFilename: 'manifest.json',
      useCredentialsForManifestTag: false,
      manifest: {
        name: 'ХичХайк',
        short_name: 'ХичХайк',
        description: 'Поиск автосервисов с реальным статусом загруженности',
        display: 'standalone',
        orientation: 'portrait',
        background_color: '#ffffff',
        theme_color: '#27126A',
        icons: [
          {
            src: 'icons/icon-128x128.png',
            sizes: '128x128',
            type: 'image/png'
          },
          {
            src: 'icons/icon-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'icons/icon-256x256.png',
            sizes: '256x256',
            type: 'image/png'
          },
          {
            src: 'icons/icon-384x384.png',
            sizes: '384x384',
            type: 'image/png'
          },
          {
            src: 'icons/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    },

    cordova: {},

    capacitor: {
      hideSplashscreen: true
    },

    electron: {
      inspectPort: 5858,
      bundler: 'packager',
      packager: {},
      builder: {
        appId: 'client-app'
      }
    },

    bex: {
      contentScripts: [
        'my-content-script'
      ],
    }
  }
});
