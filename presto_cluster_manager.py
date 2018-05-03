from fabric.api import run, env, local, cd, parallel
from fabric.decorators import roles
from fabric.operations import put
from fabric.contrib.files import exists
from fabric.tasks import execute

# """
#     usage:
#         1. 修改对应的coordinator_hosts与worker_hosts
#         2. 修改presto_install_dir与presto_backup_dir（对应服务器安装目录）
#         3. 将presto-server|client的tar包放入pack目录中
#         4. 执行 fab -f presto-cluster-tool.py deployCli|deploy|reload|start|stop|restart|rollback
#
#         deployCli:         发布presto-client
#         deploy:            发布presto集群
#         reload:            重新加载配置文件
#         start:             启动集群
#         stop:              停用集群
#         restart:           重启集群
#         rollback:          回滚操作(仅一次)
# """

# == config ==
# TODO edit your hosts
coordinator_hosts = ['fp-bd1']
worker_hosts = ['fp-bd2', 'fp-bd3', 'fp-bd4', 'fp-bd5']

presto_name = 'presto-server'
presto_tar = presto_name + "*.tar*"

# TODO edit your path
presto_install_dir = '/program'
presto_backup_dir = '/tmp/presto-backup'

env.user = 'root'
env.password = ''
env.roledefs = {
    'coordinators': coordinator_hosts,
    'workers': worker_hosts,
    'all': coordinator_hosts + worker_hosts
}

presto_cli_name = 'presto-cli'
presto_cli_jar = presto_cli_name + "*.jar"


# == each roles methods ==
def package_cli():
    local('rm -rf pack/cli/*')
    local('cp pack/' + presto_cli_jar + ' pack/cli/' + presto_cli_name)


def package_server():
    local('rm -rf pack/server/*')
    local('tar -xf pack/' + presto_tar + ' -C pack/server')


@parallel
@roles('all')
def deploy_cli_file():
    if not exists(presto_install_dir):
        run('mkdir -p ' + presto_install_dir)
    put('pack/cli/' + presto_cli_name, presto_install_dir)
    with cd(presto_install_dir):
        run('chmod +x ' + presto_cli_name)


@parallel
@roles('all')
def deploy_server_files():
    if not exists(presto_install_dir):
        run('mkdir -p ' + presto_install_dir)
    if not exists(presto_backup_dir):
        run('mkdir -p ' + presto_backup_dir)
    run('rm -rf ' + presto_backup_dir + '/*')

    is_found = str(run('ls ' + presto_install_dir + ' | grep ' + presto_name + ' && echo "found" || echo "notFound"'))
    if is_found != 'notFound':
        presto_server_names = str(run('ls ' + presto_install_dir + ' | grep ' + presto_name)).split('\r\n')
        print(presto_server_names)
        print(presto_server_names.__len__())
        if presto_server_names.__len__() > 1:
            print('error : presto-server dir is more than 1')
            print(presto_server_names)
            return
        else:
            run('mv ' + presto_install_dir + '/' + presto_name + "* " + presto_backup_dir)

    put('pack/server/*', presto_install_dir)
    with cd(presto_install_dir + '/' + presto_name + '*/bin'):
        run('chmod +x launcher')
        run('chmod +x launcher.py')


@parallel
@roles('all')
def config_server_common():
    with cd(presto_install_dir + '/' + presto_name + '*/'):
        put('config/common/etc', run('pwd'))
        run('echo "\nnode.id=' + env.host + '" >> etc/node.properties')


@parallel
@roles('coordinators')
def config_server_coordinators():
    with cd(presto_install_dir + '/' + presto_name + '*/etc/'):
        put('config/coordinator/etc/*', run('pwd'))


@parallel
@roles('workers')
def config_server_workers():
    with cd(presto_install_dir + '/' + presto_name + '*/etc/'):
        put('config/worker/etc/*', run('pwd'))


@parallel
@roles('all')
def del_server_config():
    with cd(presto_install_dir + '/' + presto_name + '*/'):
        run('rm -rf etc')


@parallel
@roles('all')
def start():
    with cd(presto_install_dir + '/' + presto_name + '*/bin'):
        run('./launcher start')


@parallel
@roles('all')
def stop():
    with cd(presto_install_dir + '/' + presto_name + '*/bin'):
        run('./launcher stop')


@parallel
@roles('all')
def restart():
    with cd(presto_install_dir + '/' + presto_name + '*/bin'):
        run('./launcher restart')


@parallel
@roles('all')
def roll_back():
    if not exists(presto_install_dir):
        print('presto_install_dir is not exists')
        return
    if not exists(presto_backup_dir + '/' + presto_name + '*'):
        print('presto backup file is not exists')
        return
    with cd(presto_install_dir):
        run('rm -rf ' + presto_name + '*')
        run('mv ' + presto_backup_dir + '/' + presto_name + '* ' + presto_install_dir)


# == avaliable methods ==
def deployCli():
    execute(package_cli)
    execute(deploy_cli_file)


def deploy():
    execute(package_server)
    execute(deploy_server_files)
    execute(config_server_common)
    execute(config_server_coordinators)
    execute(config_server_workers)


def reload():
    execute(del_server_config)
    execute(config_server_common)
    execute(config_server_coordinators)
    execute(config_server_workers)


def start():
    execute(start)


def stop():
    execute(stop)


def restart():
    execute(restart)


def rollback():
    execute(roll_back)
