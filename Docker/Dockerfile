FROM tomcat:8-jre8
MAINTAINER Medici.Yan@Gmail.com

WORKDIR /tmp

RUN set -ex \
    && rm -rf /usr/local/tomcat/webapps/* \
    && chmod a+x /usr/local/tomcat/bin/*.sh
	
COPY src/samples-web-1.4.1.war /usr/local/tomcat/webapps/ROOT.war

EXPOSE 8080
CMD ["/usr/local/tomcat/bin/catalina.sh", "run"]