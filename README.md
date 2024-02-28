# ThGen
生成Bullet Hell类型游戏画面的数据集，可用于语义分割或目标检测的训练。

## 实现方式
1. 从给定背景素材（或使用空背景）选择一张作为画布。
2. 从给定2D素材中随机选择一个，将其叠加在画布上，同时生成对应的掩码或标注框。该步骤可重复多次
3. 保存画布和对应的标签（掩码或标注框）。
4. 重复以上步骤以生成足够多的数据。

## 素材准备
### 素材文件结构
某一大类素材存放于同一个文件夹中，该文件夹下存放着该类素材的子类素材文件夹，子类素材文件夹中存放图像文件(目前仅支持png格式文件)。

以下是一种可能的素材结构：
```
.
├─background
│  ├─background1
│  │  ├───background1-1.png
│  │  └───background1-2.png
│  │      
│  └─background2
│     └───background2.png
│          
├─bullet
│  ├─bullet_heart
│  │  └───heart_yellow.png
│  │      
│  └─bullet_rice
│     ├───rice_blue.png
│     ├───rice_green.png
│     └───rice_red.png
│          
└─player
    ├─marisa
    │  └───marisa.png
    │      
    └─sanae
       ├───sanae1.png
       └───sanae2.png
```
每一大类的文件夹，可以放置在任何位置，不一定要放在同一个文件夹下。

### 背景
属于一种特殊的素材，可使用空背景(即不准备，此时默认为 768×896 大小的黑色背景)，也可使用素材，请将该类素材的目录命名为"background"（不带引号）。

请注意：背景的素材图应为RGB或RGBA格式，而其它素材图应为RGBA格式。

## 使用
### 安装依赖
```
pip install -r requirements.txt
```
### 编辑配置文件
配置文件包括了生成器的部分参数，包括素材路径、生成的数据集路径、是否禁用某些子类素材等。

启动配置编辑器：
```
python app.py
```
编辑器所用的GUI库：[PyWebIO](https://github.com/pywebio/PyWebIO)

所有的配置文件储存在config文件夹下，新建配置文件需要选择旧的配置文件进行复制。

### 运行生成器
```
python make_dataset.py --config config/your_config.json --num 1000
```
其中，--config参数指定了配置文件的路径，--num参数指定了生成的数据集大小。

最终生成的目录结构参考如下：
```
your_dataset
    ├─images
    │  ├─train
    │  │  ├───1688817526365768.jpg
    │  │  └───...
    │  │     
    │  └─val
    │     └───...
    │          
    └─labels
        ├─train
        │  ├───1688817526365768_mask.png
        │  └───...
        │      
        └─val
           └───...
```
如果为标注框模式，标签为txt文件，其格式为YOLO标注格式。

### 扩展脚本
待施工

## TODO
1. ~~将生成器整合进编辑器，使得生成器可以直接在编辑器中运行。（加了个命令行编辑器，可以执行python脚本）~~
2. ~~支持更多样化的素材平铺方式，如激光、曲线激光等。（以增加素材的方式实现，例如全屏激光可以通过直接添加全屏激光素材平铺来实现）~~
3. 支持生成视频数据集。