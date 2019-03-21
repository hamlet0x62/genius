# genius
> 精灵图书是一个书籍共享平台， 人们在这里分享、发现他们生命中的精灵。

## Features

### Main Features
  * 分享自己的书籍
  * 检索并借阅他人分享的书籍 
  * ...
 
### Another Features
  * 收藏自己想要借阅的书籍， 以便下次借阅 
  * ...
  
## Launching the app
  1. 使用git克隆本项目 
  `git clone git@github.com:oddSimond/genius.git`
  2. 使用`pipenv install` 或者 `pip install -r requirements.txt`下载依赖
  3. 使用`pipenv shell` 或者以下命令设置环境变量 
  
  ```
  # linux 下使用以下命令 
  export FLASK_APP=genius DEBUG=1 
  # windows 下使用以下命令
  set FLASK_APP=genius
  set DEBUG=1 
   ```
   
  4. 运行`flask run -p 5000`
  5. 登陆 http://127.0.0.1:5000/ 
