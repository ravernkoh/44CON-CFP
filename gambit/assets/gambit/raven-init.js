Raven.config('{% sentry_public_dsn 'https' %}', {
  release: '{{ RELEASE_HASH }}'
}).install()

Raven.setUserContext({
  username: '{{ user.username }}',
});
