 #!/bin/bash
export OS_AUTH_URL=http://192.207.61.146:5000/v2.0
export OS_SERVICE_TOKEN=a682f596-76f3-11e3-b3b2-e716f9080d50
export OS_SERVICE_ENDPOINT=http://192.207.61.146:35357/v2.0


user_id=$(keystone user-get $1 | grep -o -P 'id.{0,38}' | grep -oE '[^ ]+$')
echo $user_id