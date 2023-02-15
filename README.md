README
====

pandocでhtmlを簡単に作る。
レポートの手間をなくしつつ、きちんと記録を残そう。

## Description

仕事では、自分のやっていることを周りに理解してもらわなければ始まらない。  
かといって報告資料を作るのに時間をかけられない。むしろかけたらダメだろ。  

しかし、不十分な資料はその場しのぎにしかならず、後で見返したときに役に立たないことがある。
細かいファイルパスが書いてなかったり、貼り付けた画像の出所がわからなかったり。
自分が作った資料だった場合は「お前の資料なんだからお前が思い出せ」ということで誰も助けてくれない。
というわけで、作業方法レベルも記録しつつ、報告資料としても使えるドキュメントをmarkdownからhtml変換する環境を作った。

「htmlは報告資料じゃない」というご注文は、私の代わりにパワポ資料を作る時間を確保してくれるなら聞いてあげる。

## Usage


### md2html.py
変換対象mdファイルを引数で渡し、htmlを出力する。
`python ./md2html.py <target file>`


### cpan.py 
- ファイル または ディレクトリ を指定して md を html に変換する。
`python ./cpan.py -t <target file>`

- 実行履歴から選択する
`python ./cpan.py -l`


## Install

- windowsの場合  
[https://pandoc.org/installing.html](https://pandoc.org/installing.html) から
pandoc-*.msi をダウンロードして実行。

環境変数にpandocへのPathを通す

windows+Pause で システム設定画面を開く。  
歯車アイコンからの場合は システム > 詳細情報。  
右側の「システムの詳細設定」からシステムのプロパティ画面を開き、下方の「環境変数」から「Path」を編集し、
Pandocが入っているフォルダを追加する。  

どこにインストールされるかは、インストール時の"Advanced"オプションで確認すればOK

- Linuxの場合  
    とりあえず仕事でドキュメント作るのはwindowsなので保留




## Requirement
- python3  
    - Python 3.8.1 で動作確認
    - pandoc

## Licence

[MIT](https://github.com/shka86/foo/blob/master/LICENCE)

## Author

[shka86](https://github.com/shka86)
