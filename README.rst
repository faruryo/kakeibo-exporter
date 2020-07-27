kakeibo exporter
################

.. image:: https://codecov.io/gh/faruryo/kakeibo-exporter/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/faruryo/kakeibo-exporter

環境準備
************

#. pyenv + poetryインストール
#. Docker インストール
#. Kubernetes インストール
    * Docker for Windows/Mac の場合はKubernetes機能をオンにする。
#. GCPコンソールのIAMと管理=>サービス アカウントからサービスアカウントを作成する。ロールやユーザは紐付けなくて良い。
#. スプレッドシートの共有からサービスアカウントのアドレスを入力して共有する。
#. GCPコンソールのAPIとサービス=>認証情報から作成されたサービスアカウントで認証情報を作成し、credentials.jsonとしてREADME.rstと同階層に保存する。
#. kubectl create secret generic google-credential --from-file=./credentials.json -o yaml --dry-run=client > kubernetes/secret.yaml
#. container-structure-testをインストールする
#. 関連リソースデプロイ
    $ kubectl apply -f kubernetes

参考
======

* `2020 年の Python パッケージ管理ベストプラクティス - Qiita <https://qiita.com/sk217/items/43c994640f4843a18dbe>`_
* `Python Quickstart  |  Sheets API  |  Google Developers <https://developers.google.com/sheets/api/quickstart/python?hl=ja>`_
* `スプレッドシートをWebAPI化するサービスの作り方 - Qiita <https://qiita.com/howdy39/items/22068b3f768f0f9a757d>`_
* `Python: google-api-python-client とサービスアカウントで Google Docs のファイルをダウンロードする - CUBE SUGAR CONTAINER <https://blog.amedama.jp/entry/2019/06/06/001208>`_


サンプル
********************

* `支出管理スプレッドシートサンプル <https://docs.google.com/spreadsheets/d/106NrG6bOe3Hh3wx5iNo0_XdQ0sZuKYlJaStOHuNavAg/edit?usp=sharing>`_
    * 動作テストにも利用するので編集注意


アーキテクチャ
*****************************

クリーンアーキテクチャで構成しています。インタフェースはt-tigerさんの記事を参考に実装しています。

参考
==========

* `ラノベ風?にClean Architectureを学ぶ本【DL版】 - 飛龍さんちのフェイ＝サン - BOOTH <https://booth.pm/ja/items/1563467>`_
* `t-tiger/Python-CleanArchitecture-Example: This project is a sample Python(Flask) web application adapting Clean Architecture. <https://github.com/t-tiger/Python-CleanArchitecture-Example>`_


開発
*****************

ローカルKubernetesでの動作検証::

    $ skaffold dev --port-forward

APIは http://localhost:9000/ でアクセス可能
