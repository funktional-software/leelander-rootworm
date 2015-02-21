sudo bash

# create log directories
mkdir /var/log/pushnotifications
mkdir /var/log/agindex

# add php-curl dependency
apt-get install -y php5-curl

# set timezone
timedatectl set-timezone US/Central

#write out current crontab
crontab -l > mycron
#echo new cron into cron file

echo "0 8 * * 1-5 python /agindex/cron/AgIndex-Notification-Service/insect.py >> /var/log/pushnotifications/insect.log 2>&1" >> mycron
echo "0 0 * * * rm /var/log/pushnotifications/*" >> mycron
echo "*/5 * * * 1-5 python /agindex/cron/AgIndex-Notification-Service/test_message.py >> /var/log/pushnotifications/test.log 2>&1" >> mycron

#install new cron file
crontab mycron
rm mycron