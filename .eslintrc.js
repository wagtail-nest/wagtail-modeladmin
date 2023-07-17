module.exports = {
  extends: '@wagtail/eslint-config-wagtail',
  parserOptions: {
    ecmaVersion: 2018,
    sourceType: 'module',
  },
  rules: {
    'func-names': 'off',
    'no-param-reassign': 'off',
    'prefer-arrow-callback': 'off',
    'vars-on-top': 'off',
  },
  settings: {
    'import/resolver': {
      node: {
        extensions: ['.js', '.jsx'],
      },
    },
  },
  // ESlint default behaviour ignores file/folders starting with "."
  // https://github.com/eslint/eslint/issues/10341
  ignorePatterns: ['!.*', 'node_modules', 'dist'],
  overrides: [
    {
      files: [
        'docs/_static/**',
        'wagtail_modeladmin/static_src/wagtail_modeladmin/js/prepopulate.js',
      ],
      globals: { $: 'readonly', jQuery: 'readonly' },
    },
  ],
};
