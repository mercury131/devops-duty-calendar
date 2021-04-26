setenforce 0

yum install git nginx python3 -y

sed -i 's/enforcing/disabled/g' /etc/selinux/config

systemctl enable nginx && systemctl start nginx

#alias python=python3.6

#alias pip=pip3.6

#update-alternatives --install /usr/bin/python python /usr/bin/python2 50

#update-alternatives --install /usr/bin/python python /usr/bin/python3.5 60

#update-alternatives --install /usr/bin/pip pip /usr/bin/pip 50

#update-alternatives --install /usr/bin/pip pip /usr/bin/pip3.6 60

mkdir /var/www && chown nginx /var/www && cd /var/www

yum install gcc python3-devel openldap-devel -y

pip3.6 install uwsgi

git clone https://github.com/mercury131/flask-calendar

pip3.6 install -r flask-calendar/requirements.txt

yum remove gcc python3-devel openldap-devel -y

chown -R nginx /var/www

cp flask-calendar/uwsgi.service /etc/systemd/system/uwsgi.service && chown nginx /etc/systemd/system/uwsgi.service

systemctl daemon-reload

systemctl enable uwsgi && systemctl start uwsgi

cp flask-calendar/flask_nginx.conf /etc/nginx/conf.d/

read -p "Enter your domain FQDN: " DOMAIN -t 1 __response </dev/tty

sed -i "s|test.local|$DOMAIN|g" /etc/nginx/conf.d/flask_nginx.conf

systemctl reload nginx

firewall-cmd --zone=public --add-port=80/tcp --permanent
firewall-cmd --zone=public --add-port=443/tcp --permanent
firewall-cmd --reload

read -p "Install https access via let-s-encrypt (y/n)? " -n 1 -r -t 1 __response </dev/tty

if [[ $REPLY =~ ^[Yy]$ ]]
then

yum install certbot-nginx -y

certbot --nginx -d $DOMAIN -d www.$DOMAIN

crontab -l > mycron

echo "15 3 * * * /usr/bin/certbot renew --quiet" >> mycron

crontab mycron

rm mycron

fi


#FLASK_APP=./flask_calendar/main.py flask run --host '0.0.0.0'