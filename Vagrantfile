# -*- mode: ruby -*-
# vi: set ft=ruby :

# needed for the hyper-v stuff
Vagrant.require_version ">= 1.7.4"

Vagrant.configure("2") do |config|
  config.vm.box = "puppetlabs/ubuntu-14.04-64-puppet"
  config.vm.box_version = "= 1.0.3"

  #config.vm.network "private_network", type: "dhcp"
  
  # Use NFS for shared folders for better performance
  #config.vm.synced_folder '.', '/vagrant', nfs: true
  # port forwarding
  #config.vm.network :forwarded_port, guest: 8000, host: 8000

  config.vm.provider :virtualbox do |v, override|
  # uncomment this to debug startup problems
  #  v.gui = true

  # customize ressources
    v.memory = 4096
    v.cpus = 1
    # fast dns lookup
    #v.customize ["modifyvm", :id, "--natdnshostresolver1", "on"] #to be tested

  end

  # This is a placeholder job that can be overridden in order to install
  # puppet if needed *before* the actual provisioning happens
  config.vm.provision "provider-specific", type: :shell do |shell|
    shell.path = "deployment/providers/default.sh"
  end

  config.vm.provision :puppet do |puppet|
    puppet.environment_path = "deployment"
    puppet.environment = "testing_environment"
  end
end
