#!/usr/bin/python
#-*- coding: utf-8 -*-

from __future__ import with_statement

import yaml
from fabric.api import *
from fabric.context_managers import cd
from fabric.operations import run, sudo
from fabric.contrib import files

with open("resources/install_conf.yaml", 'r') as ymlfile:
    settings = yaml.load(ymlfile)

@task
def set_host():
    env.hosts = settings['hosts']


@task
def mkdir_working_directory():
    require('hosts', provided_by=[set_host])

    if not files.exists(settings['working_directory']):
        run("mkdir %s" % settings['working_directory'])

@task
def rm_working_directory():
    require('hosts', provided_by=[set_host])

    if files.exists(settings['working_directory']):
        run("rm -rf %s" % settings['working_directory'])


@task
def maven_install():
    mkdir_working_directory()

    with cd(settings['working_directory']):
        mvn_artefact = settings['maven']['artefact'] % settings['maven']['version']
        mvn_url = settings['maven']['url'] % (settings['maven']['version'], mvn_artefact)
        run("wget %s" % mvn_url)
        with cd("/opt"):
            sudo("tar xvzf %s/%s" % (settings['working_directory'],mvn_artefact))
            sudo("unlink maven")
            sudo("ln -s %s/apache-maven-%s maven" % ("/opt", settings['maven']['version']))
            run("export PATH=%s/%s/bin:$PATH" % ("/opt", 'maven'))
        run("rm -rf %s " % mvn_artefact)
        run("mvn -v")

@task
def java_install():
    mkdir_working_directory()
    run("apt-get install openjdk-%s-jdk" % settings['java']['version'], use_sudo=True)
    run("java -version")

@task
def liquibase_install():

    installed_liquibase = cmd('which liquibase')
    if installed_liquibase:
        install_liquibase=True
        print "Installing Liquibase %s" % settings['liquibase']['version']
    else:
        current_liquibase_version = cmd('liquibase --version')
    if current_liquibase_version != settings['liquibase']['version']:
        install_liquibase=True
        print "Updating Liquibase from %s to %s" % (current_liquibase_version, settings['liquibase']['version'])

    mkdir_working_directory()
    with cd(settings['working_directory']):
        if install_liquibase:
            liquibase_url = settings['liquibase']['url'] % (settings['liquibase']['version'], settings['liquibase']['version'])
            postgres_driver_url = settings['postgres']['driver.url'] % (settings['postgres']['driver.version'], settings['postgres']['driver.version'])
            run("wget %s" %liquibase_url)
            sudo("dpkg -i liquibase-debian_%s_all.deb" % settings['liquibase']['version'])
            if files.exists("/opt/liquibase"):
                sudo("unlink /opt/liquibase")
            sudo("ln -s /usr/lib/liquibase-%s /opt/liquibase" % settings['liquibase']['version'])
            with cd("/opt/liquibase/lib"):
                sudo("rm -rf postgresql*.jar")
                sudo("wget %s" % postgres_driver_url)
            run("rm -rf liquibase-debian_%s_all.deb" % settings['liquibase']['version'])
            current_liquibase_version = run("liquibase --version")
            print "Liquibase %s installed." % current_liquibase_version
        else:
            print "Liquibase already installed with expected version."

@task
def schemacrawler_install():
    mkdir_working_directory()

    with cd(settings['working_directory']):
        schemacrawler_url = settings['schemacrawler']['url'] % (settings['schemacrawler']['version'], settings['schemacrawler']['version'])
        run("wget %s" % schemacrawler_url)
        sudo("dpkg -i schemacrawler-deb_%s_all.deb" % settings['schemacrawler']['version'])
        sudo("mv /opt/schemacrawler/additional-lints/schemacrawler-additional-lints-*.jar /opt/schemacrawler/lib")
        sudo("chmod +rx /opt/schemacrawler/lib/schemacrawler-additional-lints-*.jar")
        run("schemacrawler --version")
        run("rm -rf schemacrawler-deb_%s_all.deb" % settings['schemacrawler']['version'])

@task
def git_install():
    sudo("apt-get -y install git git-extras")

@task
def tools_install():
    sudo("apt-get -y install filezilla")
    sudo("apt-get -y install htop")
    sudo("apt-get -y install keepassx")
    sudo("apt-get -y install terminator")
    sudo("apt-get -y install sublime-text")
    sudo("add-apt-repository ppa:webupd8team/atom")
    sudo("apt-get -y install atom")
    sudo("echo deb http://repository.spotify.com stable non-free | sudo tee /etc/apt/sources.list.d/spotify.list")
    sudo("apt-get -y install spotify-client")
    sudo("apt-get -y install owncloud-client")
    sudo("apt-get -y install gimp")
    sudo("apt-get -y install vim")

@task
def bfg_repo_cleaner_install():
    mkdir_working_directory()
    with cd(settings['working_directory']):

        if files.exists("bfg-repo-cleaner"):
            run("rm -rf bfg-repo-cleaner")

        run("mkdir bfg-repo-cleaner")
        version = settings['bfg_cleaner']['version']
        with cd("bfg-repo-cleaner"):
            bfg_url = settings['bfg_cleaner']['url'] % (version, version)
            run("wget %s -O bfg.jar" % bfg_url)
            sudo("chmod +x bfg.jar")

@task
def fakeSMTP_install():
    mkdir_working_directory()
    with cd(settings['working_directory']):
        if files.exists("fakeSMTP"):
            run("rm -rf fakeSMTP")
        run("mkdir fakeSMTP")
        with cd("fakeSMTP"):
            run("wget %s" % settings['fakeSMTP']['url'])
            run("unzip fakeSMTP-latest.zip ")
            run("mkdir received-emails")


@task
def intellij_install():
    mkdir_working_directory()

    with cd(settings['working_directory']):
        intellij_artefact = settings['intellij']['artefact'] % settings['intellij']['version']
        intellij_url = settings['intellij']['url'] % intellij_artefact
        if not files.exists(intellij_artefact):
            run("wget %s" % intellij_url)
        run("tar xvzf %s" % intellij_artefact)
        if files.exists("intellij"):
            run("unlink intellij")
        run("ln -s %s intellij" % settings['intellij']['build'])
        run("rm -rf %s" % intellij_artefact)


@task
def oh_my_zsh_install():
    with cd("~"):
        run("wget https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh -O -")

@task
def apache_directory_studio_install():
    mkdir_working_directory()

    with cd(settings['working_directory']):

        version = settings['ads']['version']
        ads_artefact = settings['ads']['artefact'] % version
        ads_url = settings['ads']['url']  %(version, ads_artefact)

        run("wget %s" % ads_url)
        if files.exists("ApacheDirectoryStudio"):
            run("rm -rf ApacheDirectoryStudio")
        run("tar xvzf %s" % ads_artefact)

        run("rm -rf %s" % ads_artefact)

@task
def apache_tomcat_install():
    mkdir_working_directory()

    with cd(settings['working_directory']):
        version = settings['tomcat']['version']
        artefact = settings['tomcat']['artefact'] % version
        major = settings['tomcat']['major']
        url = settings['tomcat']['url'] % (major, version, artefact)

        if not files.exists(artefact):
            run("wget %s" % url)

        if files.exists("tomcat"):
            run("rm -rf tomcat")

        run("tar xvzf %s" % artefact)
        run("ln -s apache-tomcat-%s tomcat" % version)

        postgres_driver_url = settings['driver']['postgres.url'] % (settings['driver']['postgres.version'], settings['driver']['postgres.version'])
        h2_driver_url = settings['driver']['h2.url'] % (settings['driver']['h2.version'], settings['driver']['h2.version'])
        javax_mail_url = settings['javax.mail']['url'] % (settings['javax.mail']['version'], settings['javax.mail']['version'])
        jt400_url = settings['driver']['jt400.url'] % (settings['driver']['jt400.version'], settings['driver']['jt400.version'])
        activation_url = settings['activation']['url'] % (settings['activation']['version'], settings['activation']['version'])

        with cd(settings['./tomcat/lib']):
            run("wget %s" % postgres_driver_url)
            run("wget %s" % h2_driver_url)
            run("wget %s" % javax_mail_url)
            run("wget %s" % jt400_url)
            run("wget %s" % activation_url)


@task
def edit_oh_my_zsh_rc():
    with cd("$HOME"):
        f = open(".zshrc","r+")
        old_lines = f.readlines()
        f.seek(0)

        for line in old_lines:
            if line == "plugins=(git)":
                f.write("plugins=(%s)" % settings['oh-my-zsh']['plugins'])
            else:
                f.write(line)

        #Add our own alias
        #java
        f.write("## PATH")
        f.write("# JAVA")
        java_path = run("which java")
        f.write("export JAVA_HOME=%s" % java_path.replace('/jre/bin/java',''))
        f.write("export PATH=$JAVA_HOME/bin:$PATH")
        f.write("export JAVA_OPTS=\"-Xms1024m -Xmx20000m\"")

        #maven
        f.write("# MAVEN")
        f.write("export MAVEN_HOME=/opt/maven")
        f.write("export PATH=$PATH:$MAVEN_HOME/bin")
        f.write("export MAVEN_OPTS=\"-Xmx1024m\"")

        #intellij
        f.write("# INTELLIJ")
        f.write("export INTELLIJ_HOME=%s/intellij" % settings['working_directory'])
        f.write("export PATH=$PATH:$INTELLIJ_HOME/bin")

        #tomcat
        f.write("# TOMCAT")
        f.write("export CATALINA_HOME=%s/tomcat")
        f.write("export CATALINA_OPTS=\"$CATALINA_OPTS -Xms256m\"")

        #liquibase
        f.write("# LIQUIBASE")
        f.write("export LIQUIBASE_HOME=/opt/liquibase")
        f.write("export PATH=$PATH:$LIQUIBASE_HOME")

        #ant
        # f.write("# ANT")
        # export ANT_HOME=/opt/ant
        # export ANT_OPTS="-Dfile.encoding=utf-8"
        # export PATH=$ANT_HOME/bin:$PATH

        #proxy settings
        f.write("# PROXY")
        proxy_addr = "http://%s:%s@%s:%s" %(settings['proxy']['username'], settings['proxy']['pwd'], settings['proxy']['host'], settings['proxy']['port'])
        f.write("no_proxy=localhost,127.0.0.1,172.16.0.0/12,10.0.0.0/8,*.site-mairie.noumea.nc,`/bin/hostname`")
        f.write("http_proxy=%s" % proxy_addr)
        f.write("https_proxy=%s" % proxy_addr)
        f.write("ftp_proxy=%s" % proxy_addr)
        f.write("export http_proxy")
        f.write("export https_proxy")
        f.write("export ftp_proxy")
        f.write("export no_proxy")
        f.write("export HTTP_PROXY=$http_proxy")
        f.write("export HTTPS_PROXY=$https_proxy")
        f.write("export FTP_PROXY=$ftp_proxy")

        f.write("## CUSTOM ALIAS")
        f.write("alias ll=\"ls -ltr\"")
        f.write("alias squirrel=\"/opt/squirrel/squirrel-sql.sh\"")
        f.write("alias fakeSMTP=\"sudo java -jar %/fakeSMTP/fakeSMTP-%s.jar -o . %/fakeSMTP/received-emails  -a 127.0.0.1\"")
        f.write("alias px='ps auxf | grep -v grep | grep -i -e VSZ -e'")
        f.write("alias df='pydf'")
        f.write("alias hist='history | grep'")
        f.write("#Apache Directory Studio")
        f.write("alias ads=\"%s/apacheDirectoryStudio/ApacheDirectoryStudio\"" % settings['working_directory'])
        f.write("#Datastudio")
        f.write("alias datastudio=\"%s/DevTools/datastudio/datastudio.sh\"" % settings['working_directory'])
        f.write("#Intellij")
        f.write("alias intellij=\"$INTELLIJ_HOME/bin/idea.sh\"")

        f.write("# Docker")
        f.write("# Kill all running containers.")
        f.write("alias dockerkillall='docker kill $(docker ps -q)'")
        f.write("# Delete all stopped containers.")
        f.write("alias dockercleanc='printf \"\n>>> Deleting stopped containers\n\n\" && docker rm $(docker ps -a -q)'")
        f.write("# Delete all untagged images.")
        f.write("alias dockercleani='printf \"\n>>> Deleting untagged images\n\n\" && docker rmi $(docker images -q -f dangling=true)'")
        f.write("# Delete all stopped containers and untagged images.")
        f.write("alias dockerclean='dockercleanc || true && dockercleani'")
        f.write("# Get image ip")
        f.write("alias dps=\"docker ps -q | xargs docker inspect --format '{{ .Id }} - {{ .Name }} - {{ .NetworkSettings.IPAddress }}'\"")
        f.write("# BFG Repo-Cleaner")
        f.write("alias bfg=\"java -jar %s/bfg-repo-cleaner/bfg.jar &&\"" % settings['working_directory'])

        f.close()
