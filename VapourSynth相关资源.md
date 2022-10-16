### VapourSynth相关资源

本文源地址是[这里](https://passthepopcorn.me/forums.php?action=viewthread&threadid=39415&postid=1908928#post1908928)，收集了VapourSynth的插件包与学习资源，基于DeepL翻译为中文，并进行了校对。

请注意，VapourSynth*不仅仅*是AviSynth(+)的一个Linux替代品。像AviSynth+一样，它可以在Linux、Windows和MacOS上运行。
对于Linux用户来说，Arch Linux是推荐的发行版，因为它有非常棒的社区支持和易用性。



#### 1. 插件

- [VapourSynth Plugins Database](https://vsdb.top/)：列出了大多数插件和模块的独特功能。
- [VapourSynth Scriptorium](https://silentaperture.gitlab.io/mdbook-guide/scriptorium.html)：列出了大多数对我们有用的插件和模块。
- [Arch User Repository](https://aur.archlinux.org/packages/?O=0&K=vapoursynth-plugin)：Arch Linux在VS压制员中非常流行，所以AUR可以用来安装大多数插件。
- [VSRepoGUI](https://forum.doom9.org/showthread.php?t=176313)：仅支持Windows的用于安装VapourSynth插件和模块的图形用户界面(GUI)。支持大多数知名的插件，但不支持一些重要的插件，如awsmfunc。
- [VapourSynth Resources](https://github.com/theChaosCoder/vapoursynth-portable-FATPACK)：仅适用于Windows的绿色版插件包。目前已经非常过时，所以只推荐作为最后的手段。

> [#1927991](https://passthepopcorn.me/forums.php?action=viewthread&threadid=39415&postid=1927991#post1927991)  lvlevvx：对于Windows用户，我想提供一个可移植的懒人包链接（Python+VapourSynth+数百个插件+2个编辑器）
>
> 由于许多原因，安装VS和它的插件可能是困难的。然而，这个便携包对我来说效果很好，我目前正在用它来编码视频。我能够在本地将python升级到3.9，我也能够更新Vapoursynth和所有插件。我还可以通过pip安装新的插件（比如AHD的[awsmfunc](https://git.concertos.live/AHD/awsmfunc)）
>
> 例如，安装awsmfunc插件，不要忘记安装它的依赖项。
>
> ```shell
>python.exe -m pip install https://git.concertos.live/AHD/awsmfunc/archive/master.zip
> ```
> 
> 我也能够在Windows上使用[vstest](https://git.concertos.live/stargaze/vstest)这个懒人包。
>
> 如果你遇到任何导入问题，只需删除`Lib\site-packages`中的vapoursynth pip包（因为它已经在父文件夹中）。



#### 2. 指南

- [VapourSynth Documentation](https://www.vapoursynth.com/doc/)：官方文档。
- [SilentAperture Guide](https://silentaperture.gitlab.io/mdbook-guide)：涵盖了实际编码中的大部分重要主题。
- [Irrational Encoding Wizardry Fansubbing Guide](https://guide.encode.moe/encoding/preparation.html)：动漫编码的小白指南。在这里列出的东西都是很好的资源。
- [Advanced x264 Encoding Guide (Linux): VapourSynth](https://passthepopcorn.me/wiki.php?action=article&id=272)：不太深入的指南。大多数VapourSynth特定的部分也可以应用于其他操作系统。请注意，sgvsfunc的每一个实例都应该被awsmfunc所取代! 一个部分的重写可以在[这里](https://git.concertos.live/AHD/EncodingGuideVapourSynth)找到。【译注：其实已经很深入了，那篇文章主体部分其实也是这个人写的，“不太深入”只是他的自谦之词】



#### 3. 预览器

- [vspreview](https://github.com/Irrational-Encoding-Wizardry/vs-preview/)：一个强大的预览器，需要一个单独的IDE来编辑脚本（例如vim、VSCode）。推荐给那些适应使用独立IDE的人。
- [VSEdit](https://github.com/YomikoR/VapourSynth-Editor/releases/) ：VapourSynth最流行的预览器，更类似于avspmod。推荐给那些想要更多的一体化解决方案的人。
- [vspreview-rs](https://github.com/quietvoid/vspreview-rs/)：极简的预览器，也需要一个单独的IDE。有时会有BUG。
- [Yuuno](https://yuuno.encode.moe/)：支持VapourSynth的Jupyter扩展。可用于方便地进行远程调试滤镜和编码。 参阅[VapourSynth Resources - Post #1954114](https://passthepopcorn.me/forums.php?action=viewthread&threadid=39415&postid=1954114#post1954114).

> 更新了 Yuuno Docker 镜像 https://hub.docker.com/r/emusysmaker/vsyuuno
>
> 主要变化:
>
> - Python 3.10 + Vapoursynth R58
> - 各种脚本和插件的最新版本
> - Jupyter Lab (从 Jupyter Notebook升级)
>
>
> 还是那句话，如果你看到缺失的属性错误，请把你使用的函数/脚本发给我，我看看是否可以把依赖关系包括进去。

- [AvsPmod](https://github.com/gispos/AvsPmod/releases)：AvsPmod也适用于VapourSynth。



#### 4. 注意事项

- 内存耗尽：如果你发现你在运行你的编码时，内存很快就用完了，试着在你的脚本中加入以下内容:


```python
core.max_cache_size=1024
```

​		限制VapourSynth脚本可以使用的线程数也会有帮助:

```python
core.num_threads = 4
```

- 独立的VapourSynth模块路径 [VapourSynth Resources - Post #1908928](https://passthepopcorn.me/forums.php?action=viewthread&threadid=39415&postid=1908928#post1908928)


> [shiki](https://passthepopcorn.me/user.php?id=118070)：astonmartin34 写道: 
>
> > 如果有些vapoursynth库你不能（或不想）在系统范围内安装（例如通过AUR），在你的项目文件夹下有一个名为 "libs "的目录，把它们都放在里面是很有用的。VSEdit有内置的能力来使这些东西可用：只要在设置中把路径添加到你的 "VapourSynth插件路径 "中。如果你需要从终端运行像vspipe这样的东西，只要在它前面加上PYTHONPATH环境变量来设置你的库的路径，像这样：
> >
> > ```bash
> > PYTHONPATH=/home/am34/vapoursynth/libs vspipe example.vpy - --y4m | x264
> > ```
>
> 或者在你的脚本顶部放上类似这样的东西：
>
> > ```python
> > import sys
> > sys.path.insert(0, "/home/am34/vapoursynth/libs")
> > ```



- [AviSynth - VapourSynth equivalent functions](http://www.vapoursynth.com/doc/avisynthcomp.html)

​		对于那些想从AviSynth过渡到VapourSynth的人来说，这个页面列出了许多AviSynth函数在VapourSynth中的对应关系。

- 
  在Windows 7上运行VapourSynth——由于Python 3.9不支持Windows 7，官方放弃了对它的支持。然而，你可以回滚Python 3.9版本的碰撞提交，并自己编译VS以使其运行。 [参阅这里](https://github.com/vapoursynth/vapoursynth/issues/677)。


- VSCode的自动完成和提示等：[VapourSynth Resources - Post #1916683](https://passthepopcorn.me/forums.php?action=viewthread&threadid=39415&postid=1916683#post1916683)


> [https://github.com/SaltyChiang/VapourSynth-Plugins-Stub-Generator](https://github.com/SaltyChiang/VapourSynth-Plugins-Stub-Generator)
>
> 对于那些在通用IDE（vscode, sublime, ect）中编写脚本的人，你可能要考虑使用一个存根文件(stub file)来实现插件的自动完成和提示。这个文件基本上只是一个你所安装的插件和相应参数的长列表。
>
> 对于我的设置，一旦生成了上述文件，我就可以把`python.analysis.stubPath`（Pylance）指向它的位置，结果就是:
>
> ![https://images2.imgbox.com/cb/ee/Wo9vjdFl_o.png](https://images2.imgbox.com/cb/ee/Wo9vjdFl_o.png)
>
> 我还创建了一个基本任务，可以运行它来重新生成文件（例如，在更新或安装新插件之后）。也许可以让它作为你的预览器的一个依赖项来运行。
>
> ```json
> {
>     "name": "VS update stubs",
>     "type": "python",
>     "request": "launch",
>     "console": "integratedTerminal",
>     "program": "/foo/bar/VapourSynth-Plugins-Stub-Generator/vs_plugins_helper.py"
> }
> ```

- [vstest](https://git.concertos.live/OpusGang/vstest)：一个非常有用的脚本来帮助测试编码器设置。



#### 5. 编码脚本示例

很多VapourSynth压制员的脚本都可以在公共资源库中找到。

- https://git.concertos.live/OpusGang/EncodeScripts - 欢迎投稿！
- https://github.com/Ichunjo/encode-scripts
- https://github.com/LightArrowsEXE/Encoding-Projects
- https://github.com/Beatrice-Raws/encode-scripts
- https://github.com/Setsugennoao/Encoding-Scripts
- https://github.com/RivenSkaye/Encoding-Progress