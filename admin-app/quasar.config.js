/* eslint-env node */

const { configure } = require('quasar/wrappers');

module.exports = configure(function (/* ctx */) {
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
        API_URL: process.env.API_URL || 'http://127.0.0.1:8000/api/v1'
      }
    },

    devServer: {
      open: true,
      port: 9001
    },

    framework: {
      config: {},

      plugins: [
        'Notify',
        'Dialog',
        'Loading'
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
        appId: 'admin-app'
      }
    },

    bex: {
      contentScripts: [
        'my-content-script'
      ],
    }
  }
});
