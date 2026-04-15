# Python 项目规范

---

## 项目结构

python项目通常应当使用下文所述的目录结构进行组织。

在icode上创建新代码库时，选择语言为python，并勾选"使用既定的配置文件初始化代码库"，将会自动生成（不使用pbr）。

也可以手动根据模板库中相关样例进行生成。

普通项目不需要使用pbr工具，大型项目可以考虑使用pbr进行版本管理和打包工作。

---

## ci.yml

用于描述编译逻辑的yaml格式配置文件（代替伪BCLOUD），配置了此文件后才能在agile上创建编译任务。

ci.yml的相关介绍见这里，以下给出python项目的ci.yml配置样例说明。

```yaml
Global:
 tool: build_submitter

Default:
 profile: [publish]

Profiles:
 - profile:
   name: dev
   env: cmc_standard
   command: python setup.py bdist_wheel
   release: false

 - profile:
   name: publish
   env: cmc_standard
   command: python setup.py bdist_wheel
   release: true
```

**说明**：

- **env** 是编译环境类型
  - 建议配置为 `cmc_standard`，这是非C/C++项目的标准环境
  - 系统环境是 centos6u3
  - 提供了各版本python、java、node、php等语言的支持
  - python版本建议通过配置 `.python-version` 文件进行指定
  - 所有版本的python都预装了pip、setuptools、virtualenv、wheel等打包时常用的基础库
  - 自动对接了百度官方的pip源、maven库等
  - 也可以配置为 `centos4u3`、`centos6u3` 或其他C/C++编译环境，但其python版本为系统自带版本（python2.3.4或python2.6.6）且没有pip命令和wheel等基础库

- **command** 是实际的打包命令
  - 建议使用 `bdist_wheel` 打包成whl文件，而不是用 `sdist` 打包成tar.gz，从而在包中保留更多的信息
  - 需要支持easy_install安装的库（通常是会被别人在setup_require中依赖的用于编译和打包的库），可以使用 `python setup.py bdist_wheel sdist` 同时创建两种格式的包
  - 如果有更复杂的打包逻辑，也可以自行编写 `build.sh` 进行实现，并在command中配置 `sh -x build.sh`

---

## .python-version

用于描述python项目开发和编译环境默认使用的python版本的隐藏文件，通常应当配置为 `2.7.14`。

目前支持 `2.7.14`、`3.5.5`、`3.6.5`，有更多版本需求的请联系 pip@baidu.com。

```
2.7.14
```

有些项目可能同时兼容py2和py3，或者属于py2和py3的混合项目，可以将需要使用的版本全部写入 `.python-version` 文件中，每行一个版本号。

多版本的 `.python-version`：

```
2.7.14
3.5.5
3.6.5
```

这样，这些python将同时可用，可以通过 `python2.7`、`python3`、`python3.5`、`python3.6` 之类的命令来调用指定版本。

---

## setup.py

python项目打包脚本，但不建议将具体的项目信息写在setup.py中，而是使用setup.cfg进行配置。

setup.py建议统一按如下样例进行配置，根据是否使用pbr进行打包有两种不同的写法。

大部分项目无需使用pbr，setup.py配置方法可以参考如下样例：

```python
#!/usr/bin/env python
# -*- coding: UTF-8 -*-

################################################################################
#
# Copyright (c) 2018 Baidu.com, Inc. All Rights Reserved
#
################################################################################

"""
Setup script.

Authors: liushuxian(liushuxian@baidu.com)

Date: 2018/02/09
"""

import setuptools


# 要求编译机器上安装的setuptools版本必须不低于30.0.0

setuptools.setup()
```

部分大型项目可以选用pbr，则按如下样例进行配置。

---

## setup.cfg

打包配置文件，包含该项目的所有信息，根据是否使用pbr进行打包有两种不同的写法。

大部分项目无需使用pbr，setup.cfg配置方法可以参考这里以及下面的样例：

```ini
[metadata]
# 项目名称，发布、安装时以此作为包名
name = hello-world
# 作者姓名和邮箱地址
author = liushuxian
author_email = liushuxian@baidu.com
# 项目版本号，1.0以上版本才视为正式版
# 当项目正式发布时应当将版本号修改到1.0以上，且应当遵守版本号规范
version = 0.1.0
# 项目概要描述信息，一句话让用户明白项目概要，不支持中文
description = Hello World
# 项目的详细描述内容和格式，包括readme和changelog等，通常使用md或rst等格式
long_description = file: README.md, CHANGELOG.md
long_description_content_type = text/markdown
# 项目的home页，通常设置为代码库地址，也可以设置为wiki或其他文档url
home_page = http://icode.baidu.com/repo/baidu/repo-skel/python/
# 开源授权协议，非对外开源的项目无需关注
license = MIT
# 项目类别，非对外开源的项目无需关注
# 从PyPI官方给出的列表中选择符合的内容进行填写
# https://pypi.org/pypi?%3Aaction=list_classifiers
classifier =
    Private :: Do Not Upload
    Programming Language :: Python
    Programming Language :: Python :: 2
    Programming Language :: Python :: 2.7
# 关键字，用于检索，方便用户搜索到你的项目
keywords =
    baidu
    demo

[options]
# 包名称，find:表示自动寻找，可在options.packages.find中进行详细配置
packages = find:
# 依赖管理，每行一个依赖库，只写直接依赖，无需考虑间接依赖
# 在这里指定的版本限制应当尽量抽象，通常只要指定最低版本和大版本号即可
install_requires =
    pip >= 9.0.1, < 10
# 单测代码目录
test_suite = hello_world.tests
# 自动添加被版本控制的数据文件
include_package_data = True
# 项目是纯py项目，可以直接执行zip源码包
zip_safe = False

[options.packages.find]
exclude =
    hello_world.excluded

[options.entry_points]
# 项目可以通过以下配置将指定的函数变成命令行工具，允许用户直接执行
console_scripts =
    hello-world = hello_world.cmdline:main

[sdist]
dist_dir = output/dist

[bdist_wheel]
dist_dir = output/dist

[easy_install]
# 使用百度官方pip源
index_url = http://pip.baidu.com/root/baidu/+simple/
```

**各项配置含义**：

- **classifier**：项目类型描述，可以从 PyPI 官方选择合适的进行填写

部分大型项目可以选用pbr，则按如下样例进行配置。

---

## requirements.txt

项目依赖列表，一个项目中往往会使用其他项目的lib或第三方库，应当统一配置在此文件中，严禁重复上传源码。

requirements.txt建议统一按如下样例进行配置，根据是否使用pbr进行打包有两种不同的写法。

大部分项目无需使用pbr，requirements.txt配置方法可以参考如下样例，不包含具体的依赖列表（实际依赖写在setup.cfg中）：

```
# 指定pip源的地址，推荐使用百度官方pip源，支持所有第三方库和百度内部发布的项目
# 如果仅依赖第三方库，也可以使用http://pypi.baidu.com/simple/ 作为源，更加稳定，但不包含任何百度内部项目
--index-url http://pip.baidu.com/root/baidu/+simple/

# 依赖当前目录中涉及的依赖，以便支持使用pip基于源码安装当前项目
-e .
```

部分大型项目可以选用pbr，则按如下样例进行配置，需要包含具体的依赖列表。

---

## project/

项目代码目录，实际名称根据项目名称而定，该项目中所有代码都必须放置在此目录下。

特别地，如果本项目是一个lib，建议将其放在 `baidu` 名空间下面，避免与开源社区的项目冲突，也方便使用方明确地知道该项目是百度内部项目。

具体的方法是：

1. 在项目代码库根目录创建一个名为 `baidu` 的目录
2. 将真正的项目代码目录 `project` 移动到 `baidu` 目录下面
3. 创建 `baidu/__init__.py`

为保证该项目可以被正确import，该目录下必须存在 `__init__.py`。

- 如果项目以package形式使用，应当正确维护 `__init__.py` 文件内容，保证其对外接口的稳定
- 如果项目以module形式使用，应当将 `__init__.py` 文件留空，同时保证当前目录下的各module对应文件的名称和接口稳定

---

## tests

单元测试目录，如无特殊需求，建议将单测目录放置在项目代码目录内，以便应用方二次开发时能基于原有单测进行扩展。

每个测试用例文件都应当以 `xxx_test.py` 或 `test_xxx.py` 的方式命名。

单元测试可以基于PyUnit、pytest或nose等框架进行实现。

---

## README

项目介绍文档，以下几种格式的README文件都是可以的（在setup.cfg中应当根据实际文件名正确配置description-file字段）：

- README：无格式的纯文本文档
- README.md：markdown格式的文档，易学易用的简易文档格式，icode支持在代码库web页上直接展示
- README.rst：reStructuredText格式的文档，python官方推荐的格式，但icode目前无法识别rst格式

---

## CHANGELOG

更新日志，使用pbr打包的项目，会在编译时根据commit message自动生成ChangeLog文件，无需人工维护。

但考虑到commit message往往比较混乱，可以考虑人工维护一份更可读的变更日志，建议用markdown编写，命名为 `CHANGELOG.md`。

建议基于 Keep A Changelog 的格式管理变更日志。

---

## LICENSE

授权许可文档，此文件不是必须存在的。

开源项目必须选定一个适合项目的授权许可，根据项目类型的不同，选择也会有所差异。

通常可以选择最为宽松的MIT协议。

除非你完全清楚自己的意图，否则不要采用GPL系的协议，也不要依赖GPL系的第三方库。

---

## conf/

配置目录，此目录不是必须存在的。

对于有些工具或服务程序，是有自己的配置文件的，这些文件在安装时应当自动安装，但又不适合被安装进代码目录。

可以将这些配置都放置在 `conf` 目录下，并通过setup.cfg中相关配置将其安装到 `/etc` 或 `~/.etc/` 等目录下。

---

## docs/

文档目录，此目录不是必须存在的。

开源项目应当准备充分的文档，这将有利于其他潜在贡献者为你的项目贡献代码。

python项目的文件建议通过sphinx生成文档，由于百度python编码规范约定使用google风格的注释，还需要配合napoleon扩展插件。

---

## 单元测试

python项目的单元测试框架有很多，可以根据团队习惯和项目需求进行选择，unittest、pytest、nose等框架均可，不做强制要求。

如果项目允许在多个python下运行，建议使用tox进行多版本兼容性测试，编译集群的标准python环境中已预装了tox工具。

### 编写单元测试用例

建议将测试用例目录放在项目代码中，随项目一起发布，这样用户在二次开发时也可以方便地执行你的单元测试用例。

比如，一个名为 `hello-world` 的项目，其单测目录建议是：`hello_world/tests`，而不是直接在代码库根目录创建tests目录。

以pytest为例，它对单测的要求如下（可以看出，基于unittest、nose等框架的用例，通常也都是合法的pytest用例）：

- 测试文件以 `test_` 开头（或以 `_test` 结尾）
- 测试类以 `Test` 开头，并且不能带有 `__init__` 方法
- 测试函数以 `test_` 开头
- 断言使用基本的 `assert` 即可

### 指定测试中使用的python版本

在代码库根目录下创建 `.python-version` 文件，指定测试中使用到的python版本，需要具体到小版本号。

比如，同时兼容2.7、3.5、3.6这几个版本的项目，可以像下面这样配置：

```
2.7.14
3.5.5
3.6.5
```

### 配置tox.ini文件，描述测试方法

在代码库根目录下创建 `tox.ini` 文件，详细描述测试方式。

```ini
[tox]
envlist=py27,py35,py36
skipsdist=True

[testenv]
deps=
    py{27}: mock
    pytest
    -rrequirements.txt
sitepackages=False
changedir={toxinidir}
setenv=
    LANG=en_US.UTF-8
commands=
    py.test hello_world/tests
```

**说明**：

- **envlist**：指定测试环境，根据项目实际情况填写
- **deps**：指定测试依赖，除了项目本身依赖的 `-rrequirements.txt`，还包括测试框架pytest（或nose等其他框架），测试用的mock（python3有内置mock，python2需要额外安装）
- **setenv**：设置环境变量，编译集群的默认编码不是UTF-8，可能导致某些国外的包无法安装，这里需要指定一下
- **commands**：是测试命令，每行一句命令，样例中是使用pytest执行 `hello_world/tests` 目录中所有单测用例

### 更新ci.yml，修改编译命令

带tox测试的ci.yml：

```yaml
Global:
 tool: build_submitter

Default:
 profile: [publish]

Profiles:
 - profile:
   name: dev
   env: cmc_standard
   command: tox && python setup.py bdist_wheel
   release: false

 - profile:
   name: publish
   env: cmc_standard
   command: tox && python setup.py bdist_wheel
   release: true
```

修改command命令，先执行tox进行测试，通过后才进行打包。

---

## 版本管理

### 版本号规范

python项目的版本号必须严格遵守 PEP-440 规范，并尽量到与公司产品库的4位版本号兼容。

其格式必须与以下scheme匹配。

版本号格式：

```
[N!]N(.N)*[{a|b|rc}N][.postN][.devN]
```

建议使用3位数字版本号对项目进行管理：**major.minor.patch**

- **major**：主要版本号，对外的API出现不兼容升级时，应当变更主版本号
- **minor**：次要版本号，增加新功能，或旧功能添加deprecation标识时，应当变更次要版本号
- **patch**：补丁号，每次bugfix时，应当变更补丁号

进行发布时，根据发布目标不同，可以使用不同的版本号。

- **发布到产品库**时，以全局的构建编号作为第4位版本号，组成一个4位纯数字的版本号进行发布。
- **发布到官方pip源**时，允许用以下几种版本号格式进行发布：
  - `N.N.N`：稳定版本
  - `N.N.NaN`：alpha版本，仅用于内测，可能存在大量bug和功能缺失
  - `N.N.NbN`：beta版本，仅用于公测，包含主要功能，但可能存在一些bug
  - `N.N.NcN`：候选版本，接近可发布状态，此版本下将不再添加新功能，仅做bugfix
  - `N.N.NrcN`：候选版本，含义与 `N.N.N.cN` 类似，但更接近可发布状态
  - `N.N.N.postN`：post-release版本，仅用于在N.N.N版本上更新文档，代码本身不会变化，禁止在post版本上进行bugfix
  - `N.N.N.devN`：开发版本，以上所有版本格式都可以添加 `.devN` 后缀，该版本仅会保留15天，然后就会被清理

### 版本依赖规则

python依赖总是使用pip或easy_install访问官方pip源进行安装。

#### 筛选规则

默认情况下，只会安装稳定版本：即 `N.N.N` 版本。

安装稳定版本：

```
pip install setuptools
pip install 'setuptools==38.0'
pip install 'setuptools>=38.0'
```

当显式指定了带有 `.dev` 或其他特殊后续的版本号时，或者pip命令使用了 `--pre` 参数时，才会安装dev或alpha、beta、candidate版本。

安装pre版本：

```
pip install --pre setuptools
pip install 'setuptools>=38.0.dev1'
```

#### 排序规则

pip默认总是安装最新版本，而详细指定版本范围时也会涉及到版本号的排序，其排序规则可以参考以下样例：

```python
from verlib import NormalizedVersion as V

assert (
 V('1.0a1')
 < V('1.0a2.dev456')
 < V('1.0a2')
 < V('1.0a2.1.dev456')
 < V('1.0a2.1')
 < V('1.0b1.dev456')
 < V('1.0b2')
 < V('1.0b2.post345')
 < V('1.0c1.dev456')
 < V('1.0c1')
 < V('1.0.dev456')
 < V('1.0')
 < V('1.0.post456.dev34')
 < V('1.0.post456'))
```

以上列出的各个版本号依次递增，很符合直觉：

- 数字版本号较小的版本一定较小
- 数字版本号相同时：alpha < beta < candidate < 稳定版本 < post

对于开发版本：

- 任何版本都大于自己的dev版本
- 当版本甲大于版本乙时，版本甲的dev版本也大于版本乙

### 版本号生成

#### 不使用pbr的项目

不使用pbr的项目需要手动维护版本号，每次发版前必须手动更新setup.cfg中的version项，也可以在提交新功能或bugfix代码的同时修改版本号。

#### 使用pbr的项目

python项目可以使用开源插件pbr来进行打包，同时也由pbr负责生成版本号。

版本可以使用两种方式管理：**postversioning** 和 **preversioning** 管理。

- **postversioning** 是默认方式，根据提交日志生成版本号
- **preversioning** 通过在setup.cfg文件的metadata项目下面设置版本信息控制，直接基于设置的版本信息生成版本号

版本号生成都是基于git中的信息，具体生成流程如下：

1. **检查tag**
   - 如果指定的commit设置了合法的tag，那么直接以这个tag作为版本号
   - 否则，我们则使用最后一次被tag记录的合法版本号，根据后续的2、3、4步骤，在其上递增获取目标版本

2. 遍历git的历史信息，直到最新的commit。在每次commit log中，我们寻找Sem-Ver信息，并对版本号进行相应的操作：
   - **apt-break**：major版本号递增
   - **feature**：minor版本号递增
   - **deprecation**：minor版本号递增
   - **bugfix**：patch号递增
   - 缺少Sem-Ver行则等同于bugfix

3. **版本号校验**
   - 如果使用postversioning模式，我们使用上一步中推导出的版本号作为目标版本
   - 如果使用preversioning模式，那就是说在setup.cfg的metadata中有设置版本信息
   - 如果该版本号大于上一步中推导出的版本号，使用setup.cfg中定义的版本号作为目标版本
   - 否则，抛出异常

4. 基于最后发布的提交，我们产生一个dev版本的字符串。然后使用目前git的sha字符串来区分多个dev版本中使用相同号码的提交

基于以上逻辑，当且仅当指定commit打了合法tag时，会在第1步中直接生成与tag一致的版本号（包括N.N.N的稳定版本或其他不稳定版本），否则，会在第4步时推导出一个 `N.N.N.devN` 格式的开发版本号。
