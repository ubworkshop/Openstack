#
# DOCKER-VERSION    1.10.3
#
# Dockerizing CentOS7: Dockerfile for building CentOS images
#
FROM daocloud.io/centos:7 

MAINTAINER liulin

ENV TZ "Asia/Shanghai"
ENV LANG en_US.UTF-8

ADD http://10.12.15.12/java/jdk-7u80-linux-x64.tar.gz /opt/
RUN cd /opt/ && tar zxf jdk-7u80-linux-x64.tar.gz
RUN rm -f /opt/jdk-7u80-linux-x64.tar.gz

ADD http://10.12.15.12/tomcat/apache-tomcat-7.0.63.tar.gz /opt/
RUN cd /opt/ && tar zxf apache-tomcat-7.0.63.tar.gz
RUN rm -f /opt/apache-tomcat-7.0.63.tar.gz

#ENV JAVA_OPTS "-server -Xms64M -Xmx1024M -XX:PermSize=64M -XX:MaxPermSize=512M"

#ADD http://10.12.15.9:8081/workspace/itamcs/target/itamcs.war /usr/local/tomcat/webapps

ENV JAVA_HOME /opt/jdk1.7.0_80
ENV CATALINA_HOME /opt/apache-tomcat-7.0.63
ENV PATH $JAVA_HOME/bin:$CATALINA_HOME/bin:$PATH
WORKDIR $CATALINA_HOME

EXPOSE 8080

RUN sed -i s/"Connector port=\"8080\""/"Connector port=\"8080\" URIEncoding=\"UTF-8\""/g $CATALINA_HOME/conf/server.xml

CMD ["catalina.sh", "run"]
