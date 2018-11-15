# presto集群管理工具
**presto-cluster-tool**

1.     support presto-0.1xx/0.2xx
			
		env: 
		  python3 + fabric1.x
         pip install 'fabric<2.0'
         pip instlal fabric3
         pip install presto-python-client
         
         see 
         http://www.fabfile.org/installing-1.x.html  
         https://pypi.org/project/presto-python-client

    
2.     usage:
		 `fab -f presto-cluster-tool.py deployCli|deploy|reload|start|stop|restart|rollback`
		 
        1. 修改脚本对应的coordinator_hosts与worker_hosts
        2. 修改脚本presto_install_dir与presto_backup_dir（对应服务器安装目录）
        3. 将presto-server|client的tar包放入pack目录中

        deployCli:         发布presto-client
        deploy:            发布presto集群
        reload:            重新加载配置文件
        start:             启动集群
        stop:              停用集群
        restart:           重启集群
        rollback:          回滚操作(仅一次)
