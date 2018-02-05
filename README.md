# netkeiba_python

# 環境
```
python >= 3.5
scrapy
```

# 実行

scrapy を使って http://db.netkeiba.com からレース情報を取得する。

```
$ cd netkeiba_python
$ scrapy crawl netkeiba -o keiba-10y.json
```
`/netkeiba_python/spiders/netkeiba_spider.py` では `DATE_MIN = 20071231` となっている。
これにより、デフォルトでは2008-2018年のレース情報を取得する。

`DATE_MIN` 変数を書き換えれば取得する期間を変更できる。

保存されたデータを加工して CSV 形式に変換する。

```
$ python jsontocsv.py
```

入出力ファイルのパスはファイルにハードコードされている（面倒臭いので）。適宜変更して使用する必要がある。

どのようなデータが得られるかは CSV のヘッダを参照すること。

