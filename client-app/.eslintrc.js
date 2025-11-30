module.exports = {
  root: true,

  parserOptions: {
    ecmaVersion: 2021
  },

  env: {
    node: true,
    browser: true,
    'vue/setup-compiler-macros': true
  },

  extends: [
    'plugin:vue/vue3-essential',
    'eslint:recommended'
  ],

  plugins: [
    'vue'
  ],

  globals: {
    process: 'readonly'
  },

  rules: {
    'prefer-promise-reject-errors': 'off',
    quotes: ['warn', 'single', { avoidEscape: true }],
    'no-unused-vars': 'warn',
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off'
  }
}
