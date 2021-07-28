
read -p "Update the DevOPS duty schedule calendar to the latest version? (y/n)? " -n 1 -r

if [[ $REPLY =~ ^[Yy]$ ]]
then

    if [ -d "../backup" ] 
    then
        echo "Directory ../backup exists." 
    else
        echo "Directory ../backup does not exists."
        echo "Create Directory ../backup."
        mkdir ../backup
    fi

    if [ -d "../backup/backup-$(date +%Y-%m-%d)" ] 
    then
        echo "Directory ../backup/backup-$(date +%Y-%m-%d) exists." 
        echo "Move Directory ../backup/backup-$(date +%Y-%m-%d) to ../backup/backup-$(date +%Y-%m-%d-%H-%M-%S)." 
        mv ../backup/backup-$(date +%Y-%m-%d) ../backup/backup-$(date +%Y-%m-%d-%H-%M-%S)
        echo "Create Directory ../backup/backup-$(date +%Y-%m-%d)."
        mkdir ../backup/backup-$(date +%Y-%m-%d)    
    else
        echo "Error: Directory ../backup/backup-$(date +%Y-%m-%d) does not exists."
        echo "Create Directory ../backup/backup-$(date +%Y-%m-%d)."
        mkdir ../backup/backup-$(date +%Y-%m-%d)
    fi

    echo "Create backup"

    cp -rf . ../backup/backup-$(date +%Y-%m-%d)

    if $(ls -la | grep -q "\->"); then
        echo "Found symlinks in main directory. Copy originals"
        mkdir ../backup/backup-$(date +%Y-%m-%d)/symlinks_originals
        for i in $(ls -la | grep "\->" | awk '{print $9}') ; do cp -r -L $i ../backup/backup-$(date +%Y-%m-%d)/symlinks_originals/ && echo "Copy $i"; done
    fi

    read -p "Backup process completed. Start update process (y/n)? " -n 1 -r

    if [[ $REPLY =~ ^[Yy]$ ]]
    then

    STATUS="$(systemctl is-active devops-duty-calendar)"
if [ "${STATUS}" = "active" ]; then
    echo "Stop devops-duty-calendar service"
    systemctl stop devops-duty-calendar
else 
    echo "devops-duty-calendar service not running "   
fi
    pip3.6 install -r devops-duty-calendar/requirements.txt
    echo "Stash your changes" 
    git stash
    echo "Pull latest version" 
    git pull
    echo "Merge your local changes with latest version" 
    git stash pop
    echo "Update completed!"
    if [[ $(systemctl list-units --all -t service --full --no-legend "devops-duty-calendar" | cut -f1 -d' ') == "devops-duty-calendar" ]]; then
        echo "Start service devops-duty-calendar"
        systemctl start devops-duty-calendar
    else
        echo "Service devops-duty-calendar not found!"
        read -p "Install the service? (y/n)? " -n 1 -r
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
            cp devops-duty-calendar/devops-duty-calendar.service /etc/systemd/system/devops-duty-calendar.service && chown nginx /etc/systemd/system/devops-duty-calendar.service
            systemctl daemon-reload
            systemctl enable devops-duty-calendar && systemctl start devops-duty-calendar
        fi

    fi


    else

        echo "!!!"
        echo "Update process aborted!"

    fi


else

    echo "!!!"
    echo "Update process aborted!"

fi