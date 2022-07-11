# myhugo

My Hugo based blog. If you are not familiar to Hugo yet, please read [an excellent tutorial](https://www.ii.com/themeless-gitless-intro-hugo).

## Installation

On Ubuntu

```bash-session
$ sudo apt-get install hugo

$ hugo version
Hugo Static Site Generator v0.68.3/extended linux/amd64 BuildDate: 2020-03-25T06:15:45Z
```

## Themes

Run the commands from the folder where README.md is.

### Clone a new theme

Find a theme at https://themes.gohugo.io/, e.g. https://github.com/mismith0227/hugo_theme_pickles

```bash-session
$ cd ./themes

$ git submodule add git@github.com-ff:mismith0227/hugo_theme_pickles.git
Cloning into '/workdir/codes/github_ff/myhugo/themes/hugo_theme_pickles'...
remote: Enumerating objects: 1908, done.
remote: Counting objects: 100% (313/313), done.
remote: Compressing objects: 100% (205/205), done.
remote: Total 1908 (delta 122), reused 219 (delta 71), pack-reused 1595
Receiving objects: 100% (1908/1908), 2.41 MiB | 476.00 KiB/s, done.
Resolving deltas: 100% (835/835), done.

$ cd ..

$ echo theme = \"hugo_theme_pickles\" >> config.toml
```

### Init themes after cloning repository

```bash-session
$ git submodule init

$ git submodule update
```

```bash-session
[submodule "themes/hugo-kiera"]
	path = themes/hugo-kiera
	url = git@github.com-ff:funkydan2/hugo-kiera.git
[submodule "themes/hugo-theme-pixyll"]
	path = themes/hugo-theme-pixyll
	url = git@github.com-ff:azmelanar/hugo-theme-pixyll.git
[submodule "themes/hugo_theme_pickles"]
	path = themes/hugo_theme_pickles
	url = git@github.com-ff:mismith0227/hugo_theme_pickles.git
[submodule "themes/hugo-theme-swift"]
	path = themes/hugo-theme-swift
	url = git@github.com-ff:foreverfaint/hugo-theme-swift.git
	branch = main
```

### Update themes

```bash-session
$ git submodule update --rebase --remote
```

### Delete a theme submodule

Please read [How do I remove a submodule?](https://stackoverflow.com/questions/1260748/how-do-i-remove-a-submodule)

```bash-session
$ git rm themes/hugo-rocinante

$ rm -rf .git/modules/themes/hugo-rocinante

$ git config --remove-section submodule.themes/hugo-rocinante
```

### Some themes I like

|Theme|hugo-theme|github|
|:---|:---|:-----|
|hugo-kiera|https://themes.gohugo.io/themes/hugo-kiera/#demo|https://github.com/funkydan2/hugo-kiera|
|hugo_theme_pickles|https://themes.gohugo.io/themes/hugo_theme_pickles/|https://github.com/mismith0227/hugo_theme_pickles|
|hugo-theme-pixyll|https://themes.gohugo.io/themes/hugo-theme-pixyll/|https://github.com/azmelanar/hugo-theme-pixyll|

## Content

## Highlight

If you run with markup.highlight.noClasses=false in your site config, you need a style sheet. More detail, please read [Syntax Highlighting](https://gohugo.io/content-management/syntax-highlighting/)

> hugo gen chromastyles --style=monokai > syntax.css

### Create New Post

```bash-session
$ hugo new posts/my-first-post.md
./content/posts/build_tensorrt_docker_image.md created
```

### Preview

```bash-session
$ hugo server -D

                   | EN  
-------------------+-----
  Pages            | 10  
  Paginator pages  |  0  
  Non-page files   |  0  
  Static files     | 22  
  Processed images |  0  
  Aliases          |  2  
  Sitemaps         |  1  
  Cleaned          |  0  

Built in 28 ms
Watching for changes in /workdir/codes/github_ff/myhugo/{archetypes,content,data,layouts,static,themes}
Watching for config changes in /workdir/codes/github_ff/myhugo/config.toml, /workdir/codes/github_ff/myhugo/themes/hugo-kiera/config.toml
Environment: "development"
Serving pages from memory
Running in Fast Render Mode. For full rebuilds on change: hugo server --disableFastRender
Web Server is available at http://localhost:1313/ (bind address 127.0.0.1)
Press Ctrl+C to stop
```

### Publish

```bash-session
$ hugo --cleanDestinationDir --minify
```