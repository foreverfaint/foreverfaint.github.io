# myhugo

My Hugo based blog.

## Installation

On Ubuntu

```bash
$ sudo apt-get install hugo

$ hugo version
Hugo Static Site Generator v0.68.3/extended linux/amd64 BuildDate: 2020-03-25T06:15:45Z
```

## Themes

Run the commands from the folder where README.md is.

### Clone a new theme

Find a theme at https://themes.gohugo.io/, e.g. https://github.com/mismith0227/hugo_theme_pickles

```bash
$ cd ./themes

$ git submodule add https://github.com/mismith0227/hugo_theme_pickles
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

### Update themes

```bash
$ git submodule update --rebase --remote
```

### Some themes I like

|Theme|hugo-theme|github|
|:---|:---|:-----|
|arabica|https://themes.gohugo.io/themes/arabica/|https://github.com/nirocfz/arabica|
|vienna|https://themes.gohugo.io/themes/vienna/|https://github.com/keichi/vienna|
|hugo-kiera|https://themes.gohugo.io/themes/hugo-kiera/#demo|https://github.com/funkydan2/hugo-kiera|
|hugo_theme_pickles|https://themes.gohugo.io/themes/hugo_theme_pickles/|https://github.com/mismith0227/hugo_theme_pickles|
|hugo-theme-pixyll|https://themes.gohugo.io/themes/hugo-theme-pixyll/|https://github.com/azmelanar/hugo-theme-pixyll|
|hugo-theme-minos|https://themes.gohugo.io/themes/hugo-theme-minos/|https://github.com/carsonip/hugo-theme-minos|
|paperback|https://themes.gohugo.io/themes/paperback/|https://github.com/dashdashzako/paperback|

## Content

```bash
$ hugo new posts/my-first-post.md
${root}/content/posts/build_tensorrt_docker_image.md created

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