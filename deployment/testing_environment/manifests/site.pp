node default {
    # needed for ruby2.4
    exec { 'apt-get install software-properties-common':
        provider => shell,
        command  => 'apt-get update && apt-get install -y software-properties-common'
    } ->
    exec { 'apt-add-repository':
        provider => shell,
        command  => 'apt-add-repository -y ppa:brightbox/ruby-ng && apt-get update'
    } ->
    exec { 'apt-get update':
        provider => shell,
        command  => 'apt-get update'
    }

    # general packages
    package { ['git', 'build-essential', 'vim']:
        ensure => installed,
    } ->
    # python packages
    package { ['python3', 'python3-dev', 'python3-pip', 'libxslt1-dev', 'zlib1g-dev', 'gettext', 'libpq-dev', 'libffi-dev', 'libssl-dev']:
        ensure => installed,
    } ->
    package { ['ruby2.4', 'ruby2.4-dev']:
        ensure => installed,
    }

    exec { 'replace bashrc':
        provider => shell,
        command  => 'cp /vagrant/deployment/testing_environment/.bashrc /home/vagrant/.bashrc' 
    } ->

    /*
    exec { 'auto_cd_vagrant':
        provider    => shell,
        command     => 'echo "\ncd /vagrant" >> /home/vagrant/.bashrc'
    }

    exec { 'alias_python_python3':
        provider    => shell,
        # the sudo thing makes "sudo python foo" work
        command     => 'echo "\nalias python=python3\nalias pip=pip3\nalias sudo=\'sudo \'" >> /home/vagrant/.bashrc'
    }
    */

    exec { 'install project deps':
        provider => shell,
        command  => 'sudo /bin/bash -c "cd /vagrant/ && ./deployment/testing_environment/installProjectDeps.sh"'
    }
}
