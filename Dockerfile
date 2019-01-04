FROM centos:7
MAINTAINER yongs2 yongs2@hotmail.com

ARG LOCALTIME=Asia/Seoul
ARG LAME_VERSION=3.100
ARG ASTERISK_VERSION=16-current
ARG ASTERISK_G729=codec_g729-ast160-gcc4-glibc-x86_64-pentium4

RUN yum -y update \
  && yum -y install epel-release \
  && yum repolist \
  && yum -y install deltarpm \
  && yum -y install \
    kernel-headers gcc gcc-c++ cpp bzip2 patch \
    ncurses ncurses-devel \
    libxml2 libxml2-devel \
    sqlite sqlite-devel \
    openssl-devel newt-devel \
    kernel-devel libuuid-devel net-snmp-devel \
    unixODBC unixODBC-devel \
    mysql-connector-odbc mysql-devel \
    libtool-ltdl libtool-ltdl-devel \
    tar make git wget file \
    speex speex-devel libsrtp libsrtp-devel sox \
    lua lua-devel unzip readline-devel \
    curl-devel libedit-devel 

RUN mkdir -p /usr/src/asterisk \
  && cd /usr/src \
  && wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-${ASTERISK_VERSION}.tar.gz \
  && tar -xzvf /usr/src/asterisk-${ASTERISK_VERSION}.tar.gz --strip-components=1 -C /usr/src/asterisk \
  && mv /etc/localtime /etc/localtime.bak \
  && ln -s /usr/share/zoneinfo/${LOCALTIME} /etc/localtime \
  && cd /usr/src/asterisk \
  && ./configure --libdir=/usr/lib64 --with-jansson-bundled --with-pjproject-bundled \
  && make menuselect.makeopts \
  && menuselect/menuselect \
    --disable BUILD_NATIVE \
    --enable res_config_mysql \
    --enable app_mysql \
    --enable CORE-SOUNDS-EN-WAV \
    --enable CORE-SOUNDS-EN-ULAW \
    --enable G711_NEW_ALGORITHM \
    --enable G711_REDUCED_BRANCHING \
    --disable cdr_pgsql \
    --disable cdr_csv \
    --disable cdr_sqlite3_custom \
    --enable res_snmp \
    --enable func_speex \
    menuselect.makeopts \
  && make && make install && make samples

RUN yum remove -y *devel \
  && yum -y autoremove \
  && yum -y clean all \
  && rm -rf /var/cache/yum \
  && rm -rf /usr/src/*

# MAX FILES UP
RUN sed -i 's/'\#\ MAXFILES\=\32768'/'MAXFILES\=\99989'/g' /usr/sbin/safe_asterisk \
  && sed -i 's/TTY=9/TTY=/g' /usr/sbin/safe_asterisk

COPY config/* /etc/asterisk/

#Expose outside volumes
VOLUME /var/log/asterisk
VOLUME /etc/asterisk
VOLUME /var/lib/asterisk

EXPOSE 5060 10000-20000/udp

# run asterisk in the foreground. 
CMD /usr/sbin/asterisk -f -vvvg
