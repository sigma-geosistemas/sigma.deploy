# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = "ubuntu/trusty64"
  config.vm.hostname = "mapport"

  # when accessing localhost in our host, it will be forwarded to the 8000 port on guest, so we can start everything
  # and still access it from out local machine
  config.vm.network "forwarded_port", host: 8001, guest: 8000

end
