
# ■■■ 萌え時計 ■■■  

## 【初めに】

本プログラムは、指定されたフォルダ内の画像を使用する時計です。  

対象となるOSはUbuntuのみです。  
動作の確認はUbuntu19.04(amd64)で行われています。  
他にLinuxMint18.3での動作も確認出来ていますが、保証するものではありません。

本プログラムは、pythonを使用して書かれています。  
GUIの部分には、python-gobjectを使用しています。  

## 【インストール/debの場合】

ダブルクリックでインストーラを起動してください。  

## 【インストール/zipの場合】

任意のフォルダを作成し、全てのファイルをそのフォルダ直下に展開してください。  
zipファイルは「Clone or Download」から「Download ZIP」で取得できます。

## 【起動方法/debの場合】

アプリケーションメニューのアクセサリよりmoeclockを指定して起動してください。  

## 【起動方法/zipの場合】

moeclock.pyをダブルクリックして起動してください。  
もしくは、任意にランチャを作成し、moeclock.pyを起動するようにしてください。  

## 【自動起動に設定する場合】

debパッケージの場合、同梱のmoeclock_autostartをコマンドとして指定してください。  
moeclockを指定すると起動時に画面サイズがデフォルトに戻ってしまいます。  

## 【使い方】

デフォルトでは、壁紙フォルダは/usr/share/backgroundsが指定されています。  
ウィンドウはリサイズすることが可能です。  
任意のサイズに指定することで、表示画像のアスペクト比を保持したまま時計表示を行います。  
※基準となるのは横幅です。  
ウィンドウ上の右クリックでいくつかの操作が可能です。  

### 1.設定  

　設定画面では以下の設定が可能です。  
　・壁紙フォルダの指定  
　　壁紙にはjpg、pngのみ使用可能です。  
　　壁紙フォルダにそれ以外の拡張子の画像が入っていても使用しません。  
　・文字フォントの指定  
　　文字フォントはフォント指定のみ有効です。  
　　太さやイタリックの指定、サイズ指定は無視されます。  
　　※指定するフォントによっては日本語表示が出来ません。  
　　　フォントにより平仮名は持っていても漢字を持っていない場合などありますのでご注意ください。  
　　　また、文字間隔がフォントにより異なるため、場合によってはふきだしに文字が収まらなかったり文字が重なる場合があります。  
　　※フォントのスタイルを選択すると、正常に選択したフォントで表示されない場合があります。  
　・曜日表示オフセット  
　　選択フォントによっては、曜日の表示位置が日付と大幅に離れたり、重なったりします。  
　　その場合には、このオフセット値を調整して、好みの位置に曜日を表示するようにしてください。  
　・スキンの選択  
　　描画用の枠などのスキンを指定可能です。  
　　スキンのフォルダを指定してください。  
　・文字色の指定  
　　任意の文字色が指定可能です。  
　　例：  
　　　moebuntu：#F366FF  
　　　Mikunchu♪：#86cecb  
　・時報音声ファイル選択  
　　時報に使用する任意の音声ファイルを選択出来ます。  
　　※WAVE形式で保存されたファイルのみ再生可能です。  
　・枠に画像を使用しない  
　　通常、枠は画像を使用しますが、この項目にチェックが入っている場合、枠はプログラムで描画するようになります。  
　　枠の色は文字色と同じになります。
　・枠線の太さ  
　　「枠に画像を使用しない」にチェックが入っている場合の枠線の太さを指定します。  
　・角丸め  
　　「枠に画像を使用しない」にチェックが入っている場合の内側の角丸めの半径を指定します。  

　・ウィンドウ枠を丸める  
　　この項目にチェックが入っている場合、角丸めの半径でウィンドウ枠の角を丸めます。  
　　この時、ウィンドウの影が消えてしまう場合があります。  
　　※WM依存。    

### 2.時報  

　チェックをすると、時報を鳴らせます。  

### 3.常に前面に

　チェックをすると、ウィンドウを常に前面に表示します。  

### 4.タイトルバーを表示する

　チェックを外すとタイトルバーを含むウィンドウマネージャの装飾が適用されなくなります。  
　ウィンドウの移動、リサイズもできなくなるので、その場合は再度チェックをして操作してください。  
　※ウィンドウの移動はAlt+F7、ウィンドウのりサイズはAlt+F8でも可能です。  
　※Ubuntu 19.04の場合、Windowsキー+左ボタンでウィンドウのドラッグが可能です。  
　※※※　注意！！　※※※  
　LinuxMint 19.2 Cinnamonエディションで本操作を実行すると動作が異常になります。  
　メニュー等の操作が不可能になり、再度タイトルバーを表示しようとしても画面上からは行えなくなります。  
　もしも実施してしまった場合、~/.config/moeclock.xmlを開き、  
　```<windowDecorate>False</windowDecorate>```を```<windowDecorate>True</windowDecorate>```  
　に変更してください。  
　--- 追記 ---  
　LinuxMint 19.2 Cinnamonエディションでも萌え時計を再起動すれば正常に動作するようです。  
　PCを再起動するか、システムモニターから萌え時計を終了し、再度起動すれば問題なくタイトルバーが消えることを確認しました。  
　とはいえ、一度異常な状態になるのは問題があると思いますので、出来ればこの機能は使用しないでください。  

### 5.ウィンドウサイズ  

　任意にウィンドウをリサイズ可能ですが、以下の5種類から選択してウィンドウサイズを指定出来ます。  
　・最小(280)  
　・小(320)  
　・中(400)  
　・大(480)  
　・特大(640)  

### 6.吹き出し位置  

　時刻表示の吹き出しを表示する位置を変更できます。  
　・左上  
　・右上  
　・左下  
　・右下 
　・プレフィクスの削除   
　吹き出し位置を選択すると、以下の動作を行うダイアログが表示されます。  
　※プレフィクスの削除の場合はダイアログは表示されません。
　・画像に吹き出し位置を保存  
　・デフォルトの吹き出し位置を変更  
　デフォルトではチェックされていますが、チェックを外すと、指定動作は実行されません。  
　画像に吹き出し位置を保存をチェックしていた場合、ファイル名に以下のプレフィックスが追加されます。  
  ※手動でファイル名の先頭に次の文字が指定されている場合も、吹き出しの位置を指定位置に表示します。  
　・--UL-- → 左上  
　・--UR-- → 右上  
　・--LL-- → 左下  
　・--LR-- → 右下  
　ex)
　--LL--moemoe.jpg  
　吹き出しは左上に表示されます。  
　未指定の場合は、メニューで選択された吹き出し位置に表示します。  

### 7.終了

　萌え時計を終了します。  

## 【カスタマイズ】

### 1.スキンの変更  

インストールフォルダ(/usr/share/moeclock/default)内の以下のファイルを置き換えることで任意の枠やロゴを指定できます。  
・frame.png  
　枠の画像です。背景表示したい部分を透過した透過PNGで作成してください。  
・logo.png  
　ロゴ画像です。右下に表示されます。サイズ制限等はありませんが、背景画像の透過が必要な場合には枠同様に透過PNGで作成してください。  
・annotation.svg  
　ふきだし画像です。デフォルトでは左下に表示されます。  
いずれのファイルも管理者権限でファイルマネージャを開くなどして、ファイルを置き換えることが可能です。  

裏技的に、新たなフォルダを作成し、上記の画像ファイルと同名のファイルを用意することで、スキンの切り替えが可能です。  
$HOMNE/.config/moeclock.xmlにskinという項目がありますので、その項目の値を新たなフォルダ名に変更することで、次回起動時より、指定されたスキンが有効になります。  
例：  
　/usr/share/moeclock/mikunchu  
を指定することで、みくんちゅ♪のスキンに切り替わります。  
※mikunchuスキンは今回同梱しています。  
TOYさん、ありがとうございます。  

### 2.時報の変更  

　インストールフォルダ(/usr/share/moeclock)内のsound.wavをWAVE形式のファイルと置き換えることにより時報をカスタマイズ出来ます。  

### 3.音声が切れる場合  

　時報の先頭部分が切れて再生される場合があります。  
　S/PDIFで現象を確認しており、その対策を実行する場合にチェックを入れてください。  

## 【制限事項】  

・最大化すると微妙なことになります。最大化しないでください。(^^;  
・最小化したときにタスクバーにタイトルバーを表示してます。DockBarXなど使用している場合に見えなくなる場合  
　がありますが、その時はタスク切換えを行うことで、通常表示に戻すことが出来ます。  

## 【ライセンス】

プログラム MIT  
スキン/アイコン by TOY(<http://moebuntu.web.fc2.com/>) is licensed under a Creative Commons Attribution 3.0 Unported License.  
時報音声ファイル Copyright © 2011 草乃さちか All Rights Reserved.  
※時報ファイルの改変および単体での再配布は許可されていません。  

## 【変更履歴】

*1.0.0.0　2011/01/09*  
　初版リリース  

*1.2.0.0　2011/01/26*  
　・時報音声ファイル選択機能追加  
　・スキン切り替え機能追加  

*1.3.0.0 2019/08/09*  
　・Python3対応  
　・ライセンス変更  

*1.4.0.0 2019/08/10*  
　・吹き出し位置変更機能追加  
　・バグ修正  

*1.4.1.0 2019/08/11*  
　・起動時に保存していたウィンドウのサイズを設定していなかった問題に対応  

*1.4.1.1 2019/08/11*  
　・1.4.1.0では問題が解決しなかったため再度修正  
　・非推奨になっているメソッドを使用していた部分を修正

*1.4.2.1 2019/08/12*  
　・S/PDIFで時報の先頭が切れて再生される場合がある問題に対応  

*.1.4.3.1 2019/08/13*  
　・タイトルバー非表示の際に次回起動時、タイトルバーの分だけ表示位置が下がる。  

*.1.4.4.1 2019/09/09*  
　・ファイル名の先頭にに指定文字が設定されている場合、吹き出し位置を指定位置に表示。  

*.1.4.4.2 2019/09/10*  
　・吹き出し位置を選択した際、画像のファイル名にプレフィックスを追加するかどうかを選択可能にした。  

*.1.4.4.3 2019/09/10*  
　吹き出し位置を選択すると、以下の動作を行うダイアログが表示されるようにした。  
　・画像に吹き出し位置を保存  
　・デフォルトの吹き出し位置を変更  

*.1.4.4.4 2019/09/11*  
　プレフィックスの変更。  
　プレフィックスの削除機能追加。  

*.1.4.5.1 2019/09/11*  
　吹き出しのサイズ変更機能追加。  

*.1.4.5.2 2019/09/11*  
　吹き出しのサイズ変更機能修正。  

*.1.4.5.3 2019/09/11*  
　吹き出し表示位置のデフォルト位置チェックのバグ修正。  

*.1.4.5.4 2019/09/12*  
　吹き出しサイズ変更の画質指定を変更。  

*.1.4.5.6 2019/09/12*  
　画像重ね合わせ処理の見直し。  
　吹き出しサイズ変更時の文字表示処理の見直し。  
　吹き出しサイズ変更を設定画面でスライダで指定するように変更。  
　吹き出し画像のSVG対応。  

*.1.4.5.7 2019/09/13*  
　日付時刻表示位置微調整  

*.1.4.5.8 2019/09/14*  
　吹き出し画像をSVGに変更 。 
　曜日の位置調整がスケーリングされていなかった問題に対応 。 

*.1.4.5.9 2019/09/14*  
　日時の表示位置計算が誤りがあったのを修正。  

*.1.4.5.11 2019/09/14*  
　日時の表示位置微調整。  

*.1.5.0.0 2019/09/20*  
　CSS対応。  
　フレームの描画対応。  

*.1.5.1.0 2019/09/20*  
　ウィンドウ枠の角丸め表示対応。  
