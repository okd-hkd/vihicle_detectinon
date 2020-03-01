FROM ubuntu:18.04
LABEL maintainer="okada.cn@gmail.com"

RUN apt-get update -y && apt-get install -y build-essential cmake \
libsm6 libxext6 libxrender-dev \
python3 python3-pip python3-dev openssh-server

COPY ./requirements.txt /app/requirements.txt

RUN mkdir /var/run/sshd

# root ユーザーに THEPASSWORDYOUCREATED というパスワードを設定している。
RUN echo 'root:THEPASSWORDYOUCREATED' | chpasswd
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login. sshd_config ファイルを強引に書き換えての設定変更。
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

CMD ["/usr/sbin/sshd", "-D"]

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

# we can point a web browser at the ip address or DNS name of 
# the docker host and access the app by
# 80:8080
# web:latest


EXPOSE 8080 22

# run sssh server
CMD ["/usr/sbin/sshd", "-D"]

ENTRYPOINT ["python3"]
CMD ["app.py"]
