module.exports = {
    apps: [{
      name: 'arsysintela',
      script: 'venv/bin/gunicorn',
      args: '--config gunicorn-cfg.py run:app',
      cwd: '/opt/arsysintela',
      env: {
        FLASK_APP: 'run.py',
        FLASK_ENV: 'production',
        DEBUG: 'False',
        ASSETS_ROOT: '/static'
      }
    }]
  }; 