include stdlib

node default {
    # needed for ruby2.4
    exec { 'apt-get install software-properties-common':
        provider => shell,
        command  => 'apt-get update && apt-get install -y software-properties-common'
    }
    exec { 'apt-add-repository':
        provider => shell,
        command  => 'apt-add-repository -y ppa:brightbox/ruby-ng && apt-get update',
        require => Exec['apt-get install software-properties-common']
    }
    exec { 'apt-get update':
        provider => shell,
        command  => 'apt-get update',
        require => Exec['apt-add-repository']
    }

     # general packages
    package { ['git', 'build-essential', 'vim', 'libxslt1-dev', 'zlib1g-dev', 'gettext', 'libpq-dev', 'libffi-dev', 'libssl-dev']:
        ensure => installed,
        require => Exec['apt-get update']
    } 

    # ruby2.4 for puppet
    package { ['ruby2.4', 'ruby2.4-dev']:
        ensure => installed,
        require => Exec['apt-get update']
    }

   
    # python packages
    package { ['python3', 'python3-dev', 'python3-pip']:
        ensure => installed,
        require => Exec['apt-get update']
    } 

    # app dependencies
    exec { 'install setuptools':
        provider => shell,
        command  => '/usr/bin/pip3 install --upgrade setuptools',
        require => Package['python3-pip']
    }
    exec { 'install dependencies':
        provider => shell,
        command  => '/usr/bin/pip3 install --upgrade -r requirements.txt',
        cwd => '/vagrant',
        timeout => 0,
        require => Exec['install setuptools']
    }

    # .bashrc
    file_line { 'jump_to_project_dir':
        path  => '/home/vagrant/.bashrc',
        line  => 'cd /vagrant',
    }
    file_line { 'alias_python3':
        path  => '/home/vagrant/.bashrc',
        line  => 'alias python=python3',
        require => Package['python3'],
    }
    file_line { 'alias_pip3':
        path  => '/home/vagrant/.bashrc',
        line  => 'alias pip=pip3',
        require => Package['python3-pip'],
    }
    file_line { 'alias_sudo_for_python':
        path  => '/home/vagrant/.bashrc',
        line  => "alias sudo='sudo '",
        require => Package['python3'],
    }
}
