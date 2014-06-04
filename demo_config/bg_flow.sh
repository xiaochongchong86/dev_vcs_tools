export LANG=en_US.utf8

prj_sp_edaijia=sp_edaijia
prj_www_edaijia=www_edaijia

prj_sp_path=/home/shawn/$prj_sp_edaijia
prj_www_path=/home/shawn/$prj_www_edaijia

server_path=/home/shawn/dev_vcs_tools/rest.py

sp_port=8080
www_port=8081

sp_web_port=8590
www_web_port=8591



echo '----------kill old----------'
ps aux|grep python |grep $server_path | awk '{print $2}' |xargs kill -9
cd $prj_sp_path
git instaweb --httpd=webrick --stop
cd $prj_www_path
git instaweb --httpd=webrick --stop



echo '----------start new----------'
cd $prj_sp_path
git instaweb --httpd=webrick -p $sp_web_port
nohup python $server_path $sp_port > ../$prj_sp_edaijia.log  2>&1 &


cd $prj_www_path
git instaweb --httpd=webrick -p $www_web_port
nohup python $server_path $www_port > ../$prj_www_edaijia.log  2>&1 &



