#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import with_statement

import yaml
from fabric.api import *
from fabric.context_managers import cd
from fabric.operations import run, sudo
from fabric.contrib import files
import setup_logging
import logging

setup_logging.setup_logging()

with open("resources/install_conf.yaml", 'r') as ymlfile:
    properties = yaml.load(ymlfile)


@task
def set_host():
    env.hosts = properties['hosts']
    env.user = properties['user']
    logging.info('Install development environment on : ' + str(env.hosts))


@task
def my_install_workstation():
    set_host()
    mkdir_working_directory()

    java_install()
    liquibase_install()
    schemacrawler_install()
    intellij_install()

    maven_install()
    git_install()
    apache_directory_studio_install()
    apache_tomcat_install()

    tools_install()
    bfg_repo_cleaner_install()
    fakeSMTP_install()

    oh_my_zsh_install()
    edit_oh_my_zshrc()


@task
def install_workstation():
    set_host()
    # mkdir_working_directory()
    #
    # java_install()
    # liquibase_install()
    # schemacrawler_install()
    #
    # maven_install()
    git_install()
    apache_directory_studio_install()
    apache_tomcat_install()

    tools_install()
    bfg_repo_cleaner_install()
    fakeSMTP_install()

    oh_my_zsh_install()
    edit_oh_my_zshrc()


@task
def mkdir_working_directory():
    require('hosts', provided_by=[set_host])

    if not files.exists(properties['working_directory']):
        run("mkdir %s" % properties['working_directory'])


@task
def rm_working_directory():
    require('hosts', provided_by=[set_host])

    if files.exists(properties['working_directory']):
        run("rm -rf %s" % properties['working_directory'])


@task
def maven_install():
    logging.info('Maven install...')

    mkdir_working_directory()

    with cd(properties['working_directory']):
        mvn_artefact = properties['maven']['artefact'] % properties['maven']['version']
        mvn_url = properties['maven']['url'] % (properties['maven']['version'], mvn_artefact)
        wget(mvn_url, properties['proxy']['host'] is not None)
        with cd("/opt"):
            sudo("tar xvzf %s/%s" % (properties['working_directory'], mvn_artefact))
            if files.exists("maven"):
                sudo("unlink maven")
            sudo("ln -s %s/apache-maven-%s maven" % ("/opt", properties['maven']['version']))
            run("export PATH=%s/bin:$PATH" % ("/opt/maven"))
        run("rm -rf %s " % mvn_artefact)
        run("mvn -v")

    logging.info('Maven installed with success...')


@task
def ant_install():
    logging.info('Ant install...')

    mkdir_working_directory()

    with cd(properties['working_directory']):
        ant_artefact = properties['ant']['artefact'] % properties['ant']['version']
        ant_url = properties['ant']['url'] % ant_artefact
        wget(ant_url, properties['proxy']['host'] is not None)
        with cd("/opt"):
            sudo("tar xvzf %s/%s" % (properties['working_directory'], ant_artefact))
            if files.exists("ant"):
                sudo("unlink ant")
            sudo("ln -s %s/apache-ant-%s ant" % ("/opt", properties['ant']['version']))
            run("export PATH=%s/bin:$PATH" % ("/opt/ant"))
        run("rm -rf %s " % ant_artefact)
        run("ant -version")

    logging.info('ant installed with success...')


@task
def java_install():
    logging.info('Java JDK install...')

    mkdir_working_directory()
    sudo("apt-add-repository -y ppa:openjdk-r/ppa")
    sudo("apt-get update")
    sudo("apt-get -y install openjdk-%s-jdk" % properties['java']['version'])
    run("java -version")

    logging.info('Java installed with success...')


@task
def liquibase_install():
    logging.info('Liquibase install...')

    with settings(warn_only=True):
        installed_liquibase = run('which liquibase')
        print str(installed_liquibase)

    if installed_liquibase.failed:
        install_liquibase = True
        current_liquibase_version = 0
        print "Installing Liquibase %s" % properties['liquibase']['version']
    else:
        current_liquibase_version = run('liquibase --version')

    if current_liquibase_version != properties['liquibase']['version']:
        install_liquibase = True
        print "Updating Liquibase from %s to %s" % (current_liquibase_version, properties['liquibase']['version'])

    mkdir_working_directory()
    with cd(properties['working_directory']):
        if install_liquibase:
            liquibase_url = properties['liquibase']['url'] % (
                properties['liquibase']['version'], properties['liquibase']['version'])
            postgres_driver_url = properties['driver']['postgres.url'] % (
                properties['driver']['postgres.version'], properties['driver']['postgres.version'])
            run("wget %s" % liquibase_url)
            sudo("dpkg -i liquibase-debian_%s_all.deb" % properties['liquibase']['version'])
            if files.exists("/opt/liquibase"):
                sudo("unlink /opt/liquibase")
            sudo("ln -s /usr/lib/liquibase-%s /opt/liquibase" % properties['liquibase']['version'])
            with cd("/opt/liquibase/lib"):
                sudo("rm -rf postgresql*.jar")
                sudo("wget %s" % postgres_driver_url)
            run("rm -rf liquibase-debian_%s_all.deb" % properties['liquibase']['version'])
            current_liquibase_version = run("liquibase --version")
            print "Liquibase %s installed." % current_liquibase_version
        else:
            print "Liquibase already installed with expected version."

    logging.info('Liquibase installed with success...')


@task
def schemacrawler_install():
    logging.info('Schemacrawler install...')

    mkdir_working_directory()

    with cd(properties['working_directory']):
        schemacrawler_url = properties['schemacrawler']['url'] % (
            properties['schemacrawler']['version'], properties['schemacrawler']['version'])
        run("wget %s" % schemacrawler_url)
        sudo("dpkg -i schemacrawler-deb_%s_all.deb" % properties['schemacrawler']['version'])
        sudo("mv /opt/schemacrawler/additional-lints/schemacrawler-additional-lints-*.jar /opt/schemacrawler/lib")
        sudo("chmod +rx /opt/schemacrawler/lib/schemacrawler-additional-lints-*.jar")
        run("schemacrawler --version")
        run("rm -rf schemacrawler-deb_%s_all.deb" % properties['schemacrawler']['version'])

    logging.info('Schemacrawler installed with success...')


@task
def git_install():
    logging.info('Git install...')
    sudo("apt-get -y install git git-extras")
    logging.info('Git installed with success...')


@task
def tools_install():
    logging.info('Tools install...')

    sudo("apt-get -y install filezilla")
    sudo("apt-get -y install htop")
    sudo("apt-get -y install keepassx")
    sudo("apt-get -y install terminator")
    # sudo("apt-get -y install sublime-text")
    # sudo("add-apt-repository ppa:webupd8team/atom")
    # sudo("apt-get -y install atom")
    # sudo("echo deb http://repository.spotify.com stable non-free | sudo tee /etc/apt/sources.list.d/spotify.list")
    # sudo("apt-get -y install spotify-client")
    sudo("apt-get -y install owncloud-client")
    sudo("apt-get -y install gimp")
    sudo("apt-get -y install vim")
    sudo("apt-get -y install unzip")

    logging.info('Tools installed with success...')


@task
def bfg_repo_cleaner_install():
    logging.info('BFG Repo Cleaner install...')

    mkdir_working_directory()
    with cd(properties['working_directory']):
        if files.exists("bfg-repo-cleaner"):
            run("rm -rf bfg-repo-cleaner")

        run("mkdir bfg-repo-cleaner")
        version = properties['bfg_cleaner']['version']
        with cd("bfg-repo-cleaner"):
            bfg_url = properties['bfg_cleaner']['url'] % (version, version)
            run("wget %s -O bfg.jar" % bfg_url)
            sudo("chmod +x bfg.jar")

    logging.info('BFG Repo Cleaner installed with success...')


@task
def fakeSMTP_install():
    logging.info('FakeSMTP install...')

    mkdir_working_directory()
    with cd(properties['working_directory']):
        if files.exists("fakeSMTP"):
            run("rm -rf fakeSMTP")
        run("mkdir fakeSMTP")
        with cd("fakeSMTP"):
            run("wget %s" % properties['fakeSMTP']['url'])
            run("unzip fakeSMTP-latest.zip ")
            run("mkdir received-emails")

    logging.info('FakeSMTP installed with success...')


@task
def intellij_install():
    logging.info('Intellij install...')

    mkdir_working_directory()

    with cd(properties['working_directory']):
        intellij_artefact = properties['intellij']['artefact'] % properties['intellij']['version']
        intellij_url = properties['intellij']['url'] % intellij_artefact
        if not files.exists(intellij_artefact):
            run("wget %s" % intellij_url)
        run("tar xvzf %s" % intellij_artefact)
        if files.exists("intellij"):
            run("unlink intellij")
        run("ln -s %s intellij" % properties['intellij']['build'])
        run("rm -rf %s" % intellij_artefact)

    logging.info('Intellij installed with success...')

@task
def datagrip_install():
    logging.info('DataGrip install...')

    mkdir_working_directory()

    with cd(properties['working_directory']):
        datagrip_artefact = properties['datagrip']['artefact'] % properties['datagrip']['version']
        datagrip_url = properties['datagrip']['url'] % datagrip_artefact
        if not files.exists(datagrip_artefact):
            run("wget %s" % datagrip_url)
        run("tar xvzf %s" % datagrip_artefact)
        if files.exists("datagrip"):
            run("unlink datagrip")
        run("ln -s DataGrip-%s datagrip" % properties['datagrip']['version'])
        run("rm -rf %s" % datagrip_artefact)

    logging.info('Datagrip installed with success...')



@task
def oh_my_zsh_install():
    logging.info('Oh My Zsh install...')

    if properties['proxy']['host'] is not None:
        proxy_addr = "https://%s:%s@%s:%s" % (
            properties['proxy']['username'], properties['proxy']['pwd'], properties['proxy']['host'],
            properties['proxy']['port'])
        run("git config --global https.proxy %s" % proxy_addr)

    with cd("~"):
        run("git clone https://github.com/robbyrussell/oh-my-zsh.git .oh-my-zsh")
        run("cp ~/.oh-my-zsh/templates/zshrc.zsh-template ~/.zshrc")
        sudo("apt-get -y install zsh")
        run("chsh -s /bin/zsh")
        # sudo("wget https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh -O -")

    logging.info('Oh My Zsh installed with success...')


@task
def apache_directory_studio_install():
    logging.info('Apache Directory Studio install...')

    mkdir_working_directory()

    with cd(properties['working_directory']):
        version = properties['ads']['version']
        ads_artefact = properties['ads']['artefact'] % version
        ads_url = properties['ads']['url'] % (version, ads_artefact)
        wget(ads_url, properties['proxy']['host'] is not None)
        # run("wget %s" % ads_url)
        if files.exists("ApacheDirectoryStudio"):
            run("rm -rf ApacheDirectoryStudio")
        run("tar xvzf %s" % ads_artefact)

        run("rm -rf %s" % ads_artefact)

    logging.info('Apache Directory Studio installed with success...')


@task
def postgresql_install():
    logging.info('PostgreSQL install...')

    ubuntu_version = properties['ubuntu']['codename']
    url = "deb http://apt.postgresql.org/pub/repos/apt/ %s-pgdg main" % ubuntu_version
    if not files.exists("/etc/apt/sources.list.d/pgdg.list"):
        sudo("touch /etc/apt/sources.list.d/pgdg.list")
    append_to_file(url, "/etc/apt/sources.list.d/pgdg.list", True)

    sudo("wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -")
    sudo("apt-get update")
    sudo("apt-get install postgresql-%s pgadmin3" % properties['postgres']['version'])

    old_pghba_postgres = "local   all             postgres                                peer"
    new_pghba_postgres = "local   all             postgres                                md5"
    old_pghba_all = "local   all             all                                     peer"
    new_pghba_all = "local   all             all                                     md5"
    sudo("sed -i 's/%s/%s/g' %s" % (old_pghba_postgres, new_pghba_postgres, ("/etc/postgresql/%s/main/pg_hba.conf" % properties['postgres']['version'])))
    sudo("sed -i 's/%s/%s/g' %s" % (old_pghba_all, new_pghba_all, ("/etc/postgresql/%s/main/pg_hba.conf" % properties['postgres']['version'])))

    sudo("service postgresql restart %s" % properties['postgres']['version'])

    sudo('echo "{username}:{password}" | chpasswd'.format(username='postgres', password= properties['postgres']['version']))
    # _run_as_pg('''psql -c "ALTER USER postgres WITH PASSWORD '%s';"''' % properties['postgres']['pwd'])


def _run_as_pg(command):
    return sudo('su - postgres %s' % command)


@task
def apache_tomcat_install():
    logging.info('Apache Tomcat install...')

    mkdir_working_directory()

    with cd(properties['working_directory']):
        version = properties['tomcat']['version']
        artefact = properties['tomcat']['artefact'] % version
        major = properties['tomcat']['major']
        url = properties['tomcat']['url'] % (major, version, artefact)

        if not files.exists(artefact):
            wget(url, properties['proxy']['host'] is not None)
            # run("wget %s" % url)

        if files.exists("tomcat"):
            run("rm -rf tomcat")

        run("tar xvzf %s" % artefact)
        run("ln -s apache-tomcat-%s tomcat" % version)

        postgres_driver_url = properties['driver']['postgres.url'] % (
            properties['driver']['postgres.version'], properties['driver']['postgres.version'])
        h2_driver_url = properties['driver']['h2.url'] % (
            properties['driver']['h2.version'], properties['driver']['h2.version'])
        javax_mail_url = properties['javax.mail']['url'] % (
            properties['javax.mail']['version'], properties['javax.mail']['version'])
        jt400_url = properties['driver']['jt400.url'] % (
            properties['driver']['jt400.version'], properties['driver']['jt400.version'])
        activation_url = properties['activation']['url'] % (
            properties['activation']['version'], properties['activation']['version'])

        with cd("./tomcat/lib"):
            wget(postgres_driver_url, properties['proxy']['host'] is not None)
            wget(h2_driver_url, properties['proxy']['host'] is not None)
            wget(javax_mail_url, properties['proxy']['host'] is not None)
            wget(jt400_url, properties['proxy']['host'] is not None)
            wget(activation_url, properties['proxy']['host'] is not None)
            # run("wget %s" % postgres_driver_url)
            # run("wget %s" % h2_driver_url)
            # run("wget %s" % javax_mail_url)
            # run("wget %s" % jt400_url)
            # run("wget %s" % activation_url)

    run("rm -rf %s" % artefact)

    logging.info('Apache Tomcat installed with success...')


def append_to_file(text, file, useSudo=False):
    cmd = "sed -i \"$ a " + text + "\" " + file
    if useSudo:
        sudo(cmd)
    else:
        run(cmd)


def put_double_quote_around_string(text, file):
    cmd = "sed 's/\b" + text + "\b/" + text + "/' -i " + file
    print cmd
    run(cmd)


def wget(url, useProxy=False):
    if useProxy:
        run("wget " + url + " -e use_proxy=yes -e http_proxy=$http_proxy")
    else:
        run("wget " + url)


@task
def edit_oh_my_zshrc():
    logging.info('Customize .zshrc file...')

    with cd("$HOME"):
        zshrc_file = ".zshrc"
        run("cp ~/.oh-my-zsh/templates/zshrc.zsh-template ~/%s" % zshrc_file)
        run("sed -i '/plugins=(git)/d' .zshrc")

        # Add our own alias
        # java
        append_to_file("# PATH\n", zshrc_file)
        append_to_file("# JAVA", zshrc_file)
        java_path = "/usr/lib/jvm/java-%s-openjdk-amd64" % properties['java']['version']
        text = "export JAVA_HOME=%s" % java_path
        append_to_file(text, zshrc_file)
        append_to_file("export PATH=##JAVA_HOME/bin:##PATH", zshrc_file)
        run("echo 'export JAVA_OPTS=\"-Xms1024m -Xmx20000m\"' >> " + zshrc_file)

        # maven
        append_to_file("# MAVEN", zshrc_file)
        append_to_file("export MAVEN_HOME=/opt/maven", zshrc_file)
        append_to_file("export PATH=##PATH:##MAVEN_HOME/bin", zshrc_file)
        run("echo 'export MAVEN_OPTS=\"-Xmx1024m\"' >> " + zshrc_file)

        # intellij
        append_to_file("# INTELLIJ", zshrc_file)
        append_to_file("export INTELLIJ_HOME=%s/intellij" % properties['working_directory'], zshrc_file)
        append_to_file("export PATH=##PATH:##INTELLIJ_HOME/bin", zshrc_file)

        # tomcat
        append_to_file("# TOMCAT", zshrc_file)
        append_to_file("export CATALINA_HOME=%s/tomcat" % properties['working_directory'], zshrc_file)
        run("echo 'export  CATALINA_OPTS=\"##CATALINA_OPTS -Xms256m\"' >> " + zshrc_file)

        # liquibase
        append_to_file("# LIQUIBASE", zshrc_file)
        append_to_file("export LIQUIBASE_HOME=/opt/liquibase", zshrc_file)
        append_to_file("export PATH=##PATH:##LIQUIBASE_HOME", zshrc_file)

        # ant
        append_to_file("# ANT", zshrc_file)
        append_to_file("export ANT_HOME=/opt/ant", zshrc_file)
        append_to_file("export PATH=##PATH:##ANT_HOME/bin", zshrc_file)

        # proxy properties
        if properties['proxy']['host'] is not None:
            append_to_file("# PROXY", zshrc_file)
            proxy_addr = "http://%s:%s@%s:%s" % (
                properties['proxy']['username'], properties['proxy']['pwd'], properties['proxy']['host'],
                properties['proxy']['port'])
            append_to_file(
                "no_proxy=localhost,127.0.0.1,172.16.0.0/12,10.0.0.0/8,*.site-mairie.noumea.nc,`/bin/hostname`",
                zshrc_file)
            append_to_file("http_proxy=%s" % proxy_addr, zshrc_file)
            append_to_file("https_proxy=%s" % proxy_addr, zshrc_file)
            append_to_file("ftp_proxy=%s" % proxy_addr, zshrc_file)
            append_to_file("export http_proxy", zshrc_file)
            append_to_file("export https_proxy", zshrc_file)
            append_to_file("export ftp_proxy", zshrc_file)
            append_to_file("export no_proxy", zshrc_file)
            append_to_file("export HTTP_PROXY=##http_proxy", zshrc_file)
            append_to_file("export HTTPS_PROXY=##https_proxy", zshrc_file)
            append_to_file("export FTP_PROXY=##ftp_proxy", zshrc_file)

        append_to_file("# CUSTOM ALIAS", zshrc_file)
        append_to_file("alias ll='ls -ltr'", zshrc_file)
        append_to_file("alias squirrel='/opt/squirrel/squirrel-sql.sh'", zshrc_file)
        append_to_file(
            "alias fakeSMTP='sudo java -jar %s/fakeSMTP/fakeSMTP-%s.jar -o . %s/fakeSMTP/received-emails  -a 127.0.0.1'" % (
                properties['working_directory'], properties['fakeSMTP']['version'], properties['working_directory']),
            zshrc_file)
        append_to_file("alias px='ps auxf | grep -v grep | grep -i -e VSZ -e'", zshrc_file)
        append_to_file("alias df='pydf'", zshrc_file)
        append_to_file("alias hist='history | grep'", zshrc_file)
        append_to_file("#Apache Directory Studio", zshrc_file)
        append_to_file("alias ads='%s/apacheDirectoryStudio/ApacheDirectoryStudio'" % properties['working_directory'],
                       zshrc_file)
        append_to_file("#Datastudio", zshrc_file)
        append_to_file("alias datastudio='%s/DevTools/datastudio/datastudio.sh'" % properties['working_directory'],
                       zshrc_file)
        append_to_file("#Intellij", zshrc_file)
        append_to_file("alias intellij='##INTELLIJ_HOME/bin/idea.sh'", zshrc_file)
        append_to_file("# BFG Repo-Cleaner", zshrc_file)
        append_to_file("alias bfg='java -jar %s/bfg-repo-cleaner/bfg.jar &&'" % properties['working_directory'],
                       zshrc_file)

        # append_to_file("# Docker", zshrc_file)
        # append_to_file("# Kill all running containers.", zshrc_file)
        # append_to_file("alias dockerkillall='docker kill $(docker ps -q)'", zshrc_file)
        # append_to_file("# Delete all stopped containers.", zshrc_file)
        # append_to_file("alias dockercleanc='printf \"\n>>> Deleting stopped containers\n\n\" && docker rm $(docker ps -a -q)'", zshrc_file)
        # append_to_file("# Delete all untagged images.", zshrc_file)
        # append_to_file("alias dockercleani='printf \"\n>>> Deleting untagged images\n\n\" && docker rmi $(docker images -q -f dangling=true)'", zshrc_file)
        # append_to_file("# Delete all stopped containers and untagged images.", zshrc_file)
        # append_to_file("alias dockerclean='dockercleanc || true && dockercleani'", zshrc_file)
        # append_to_file("# Get image ip", zshrc_file)
        # append_to_file("alias dps=\"docker ps -q | xargs docker inspect --format '{{ .Id }} - {{ .Name }} - {{ .NetworkSettings.IPAddress }}'\"", zshrc_file)

        run("sed -i 's/##/$/g' %s" % zshrc_file)

        run("source ~/%s" % zshrc_file)

    logging.info('.zshrc file customized with success...')
