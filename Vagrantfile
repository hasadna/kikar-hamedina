#-*- mode: ruby -*-
#vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

if ENV['KIKAR_HAMEDINA_PORT']
   $port = ENV['KIKAR_HAMEDINA_PORT']
else
   $port = 8000
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "kikar_base"
  config.vm.box_url = "https://s3-eu-west-1.amazonaws.com/kikar-dev/kikar_base.box"
  config.vm.network "private_network", ip: "192.168.100.100"
  config.vm.network :forwarded_port, guest: $port, host: $port, auto_correct: true

  config.vm.define :kikar do |t|
  end

  #Generate config files and initialize DB
  config.vm.provision :shell do |shell|
    shell.inline = <<-EOS
      set -e
      sudo -u postgres psql -c "DROP DATABASE IF EXISTS kikar"
      sudo -u postgres psql -c "DROP ROLE IF EXISTS kikar"
      sudo -u postgres psql -c "DROP ROLE IF EXISTS kikar_readonly"
      sudo -u postgres psql -c "CREATE USER kikar WITH PASSWORD 'kikar'"
      sudo -u postgres psql -c "CREATE USER kikar_readonly WITH PASSWORD 'kikar_readonly'"
      sudo -u postgres psql -c "ALTER USER kikar WITH SUPERUSER"
      sudo -u postgres psql -c "CREATE DATABASE kikar TEMPLATE=template0 ENCODING='UTF8' LC_CTYPE='en_US.utf8' LC_COLLATE='en_US.UTF-8'"
    EOS
  end

  # Django setup
  config.vm.provision :shell do |shell|
    shell.inline = <<-EOS
      set -e
      cd /vagrant/
      # install/update all git-hooks
      for hook in $(find git-hooks/ -type f | xargs basename)
      do
        rm -f .git/hooks/$hook;
        cp git-hooks/$hook .git/hooks/$hook;
      done
      [ ! -d log ] && mkdir log
      cd kikar_hamedina/
      [ ! -d logs ] && mkdir logs
      if [ ! -f ../devOps/kikar_setup.db.gz ];
      then
        wget https://s3-eu-west-1.amazonaws.com/kikar-dev/kikar_setup.db.gz -P ../devOps/ -q
      fi
      gunzip -c ../devOps/kikar_setup.db.gz | sudo -u postgres psql kikar
      # [ -f ../devOps/user_backup.json ] && python manage.py loaddata ../devOps/user_backup.json
      # python manage.py dumpdata --indent=4 auth > ../devOps/user_backup.json
      sudo pip install -r ../requirements/vps.txt
      python manage.py migrate
      python manage.py fetchfeedproperties -t || true
      # sudo -u postgres pg_dump kikar | gzip > ../devOps/kikar_setup.db.gz
      # python manage.py classify_and_test_autotag 1
    EOS
  end

  # Start kikar server process
  config.vm.provision :shell do |shell|
	shell.args = $port
    shell.inline = <<-EOS
      set -e
      echo 'exec python /vagrant/kikar_hamedina/manage.py runserver 0.0.0.0:'$1  > /etc/init/kikar.conf
      STATUS="$(sudo status kikar)"
      if [[ $STATUS == *"start"* ]];
      then
        restart kikar
      else
        start kikar
      fi

    EOS
  end

  # Download statuses
  config.vm.provision :shell do |shell|
    shell.inline = <<-EOS
      cd /vagrant/kikar_hamedina/
      python manage.py fetchfeedstatuses -a -f -t
    EOS
  end
end
