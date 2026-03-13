function doGet() {
  var ss = SpreadsheetApp.openById("xxxxxxxxxxxxxxxxxxxxxx");
  var sheet = ss.getSheetByName("Sheet1");
  var data = sheet.getDataRange().getValues();
  data.shift(); // ヘッダー行をスキップ

  // タイムゾーンをJSTに固定
  var TIMEZONE = "Asia/Tokyo";
  
  // 現在時刻をJST基準で取得
  var now = new Date();
  var nowJstStr = Utilities.formatDate(now, TIMEZONE, "yyyy/MM/dd HH:mm:ss");
  var nowJst = new Date(nowJstStr);

  // RSSの初期設定
  var rss = '<?xml version="1.0" encoding="UTF-8"?>';
  rss += '<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/">';
  rss += '<channel>';
  rss += '<title>サイネージ配信フィード</title>';
  rss += '<link>' + ss.getUrl() + '</link>';

  // --- フォルダの特定処理 ---
  var imagesFolder = null;
  var rootFolders = DriveApp.getFoldersByName("Signage");
  if (rootFolders.hasNext()) {
    var signageFolder = rootFolders.next();
    var subFolders = signageFolder.getFoldersByName("images");
    if (subFolders.hasNext()) {
      imagesFolder = subFolders.next();
    }
  }

  data.forEach(function(row) {
    var title = row[0];
    var text = row[1];
    var startVal = row[2];
    var endVal = row[3];
    var duration = row[4];
    var fileName = row[5];

    if (!startVal || !endVal) return; // 日付が空の場合はスキップ

    // スプレッドシートの日時をJSTとして解釈
    var startJst = new Date(Utilities.formatDate(new Date(startVal), TIMEZONE, "yyyy/MM/dd HH:mm:ss"));
    var endJst = new Date(Utilities.formatDate(new Date(endVal), TIMEZONE, "yyyy/MM/dd HH:mm:ss"));

    // 判定（JST同士で比較）
    if (nowJst >= startJst && nowJst <= endJst) {
      var imageUrl = "";
      if (fileName && imagesFolder) {
        var files = imagesFolder.getFilesByName(fileName);
        if (files.hasNext()) {
          var file = files.next();
          imageUrl = "https://drive.google.com/uc?export=view&id=" + file.getId();
        }
      }

      rss += '<item>';
      rss += '<title>' + escapeXml(title) + '</title>';
      rss += '<description>' + escapeXml(text) + '</description>';
      rss += '<duration>' + duration + '</duration>';
      rss += '<image>' + escapeXml(imageUrl) + '</image>';
      rss += '<file>' + fileName + '</file>'
      rss += '<content:encoded><![CDATA[';
      if (imageUrl) {
        rss += '<img src="' + imageUrl + '" style="max-width:100%;"><br>';
      }
      rss += '<p>' + text.replace(/\n/g, '<br>') + '</p>';
      rss += ']]></content:encoded>';
      // pubDateもJST形式の文字列表記にする
      rss += '<pubDate>' + Utilities.formatDate(startJst, TIMEZONE, "EEE, dd MMM yyyy HH:mm:ss +0900") + '</pubDate>';
      rss += '</item>';
    }
  });

  rss += '</channel></rss>';

  return ContentService.createTextOutput(rss)
    .setMimeType(ContentService.MimeType.RSS);
}

function escapeXml(unsafe) {
  if (typeof unsafe !== 'string') return unsafe;
  return unsafe.replace(/[<>&"']/g, function (m) {
    switch (m) {
      case '<': return '&lt;'; case '>': return '&gt;';
      case '&': return '&amp;'; case '"': return '&quot;'; case "'": return '&apos;';
      default: return m;
    }
  });
}
