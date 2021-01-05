# wolai-backup
一个基于python-selenium的工具来备份wolai云笔记的网页为纯离线状态

---
测试用的是Edge浏览器，需要从这里下载对应版本的 [浏览器驱动器](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)，并放到当前目录下；

Chrome浏览器同样的步骤，只需要把代码中`webdriver.Edge("msedgedriver.exe")`换成Chrome的启动器即可（未经过测试）

## Todo

* [x] 用户账户和密码的登录
* [x] 给定一个URL后，下载网页为HTML文件
	* [ ] 自动展开所有折叠列表ing
	* [ ] 删掉一些不需要的按钮和提示ing
	* [ ] 自动替换page的链接为本地链接，方便屏蔽js代码后也能点击跳转
		* [ ] 页面块
		* [ ] 通过\[\[  \]\]引用的页面块
		* [ ] 块引用块(感觉很难)
    * [ ] 自动下载静态文件
		* [ ] css类文件
		* [ ] emoji类图片文件
		* [ ] 用户上传的图片
		* [ ] api.wolai.com的自动挑个
* [ ] 批量下载所有页面
    * [x] 抓取侧边栏menu的页面id代码
    * [ ] 每个页面去抓取可能的子页面
    * [ ] 递归下载所有的页面
* [ ] 数据重新规整
	* [ ] 新建一个数据库，储存页面id和块的id，以及里面的内容
	* [ ] 一个新的UI来展示这个数据库
	* [ ] database类暂时没办法