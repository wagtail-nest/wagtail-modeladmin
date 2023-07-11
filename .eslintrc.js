module.exports = {
  parser: '@typescript-eslint/parser',
  extends: '@wagtail/eslint-config-wagtail',
  parserOptions: {
    ecmaVersion: 2018,
    sourceType: 'module',
  },
  rules: {
    '@typescript-eslint/explicit-member-accessibility': 'off',
    '@typescript-eslint/explicit-function-return-type': 'off',
    '@typescript-eslint/no-explicit-any': 'off',
    'react/jsx-filename-extension': [1, { extensions: ['.jsx', '.tsx'] }],
    'func-names': 'off',
    'no-param-reassign': 'off',
    'prefer-arrow-callback': 'off',
    'vars-on-top': 'off',
  },
  settings: {
    'import/resolver': {
      node: {
        extensions: ['.js', '.jsx', '.ts', '.tsx'],
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
        'wagtail_modeladmin/static_src/wagtailmodeladmin/js/prepopulate.js',
      ],
      globals: { $: 'readonly', jQuery: 'readonly' },
    },
  ],
};
