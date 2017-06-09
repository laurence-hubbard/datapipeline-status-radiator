export GOCD_DISABLE_SSL_CHECK=True

uwsgi --socket 127.0.0.1:8081 --py-autoreload 3 -w wsgi
