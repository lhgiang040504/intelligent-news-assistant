# Project Brief

## Muc tieu du an

`Intelligent News Assistant` la mot pipeline Python dung de:
- Lay tin tu cac RSS cua bao tieng Viet
- Loc theo chu de va khoang thoi gian
- Co gang lay noi dung day du cua bai viet
- Trich keyword, xep hang bai viet
- Xuat bao cao Markdown trong `reports/`

Project duoc to chuc theo kieu module hoa: moi nhom file giai quyet mot buoc ro rang trong pipeline.

## Cach tiep can cua project

Huong tiep can hien tai la pipeline rule-based, khong phu thuoc LLM trong luong chay chinh:

1. Chon nguon RSS theo topic.
2. Doc RSS moi nhat tu 3 bao: `VnExpress`, `Thanh Nien`, `Tuoi Tre`.
3. Luu du lieu raw theo tung nguon vao `data/raw/`.
4. Loc bai viet theo:
   - keyword cua topic
   - cua so thoi gian `--days` hoac `--from/--to`
5. Voi moi bai da loc, scrape them noi dung full article tu trang goc neu lay duoc.
6. Luu du lieu da xu ly vao `data/processed/`.
7. Tinh keyword noi bat bang cach gan TF-IDF don gian tren tap bai viet.
8. Xep hang bai viet theo tong trong so keyword xuat hien.
9. Tao executive summary va report Markdown.

Y nghia cua cach tiep can nay:
- Don gian, de mo rong
- Khong can API key de chay pipeline chinh
- De thay doi tung buoc rieng le nhu collector, filter, ranking, summary

## File nao lam gi

### Entry point

- `main.py`
  - Diem bat dau cua CLI.
  - Doc tham so `--topic`, `--days`, `--from`, `--to`.
  - Tao `Settings`, goi `NewsPipeline.run()`.
  - Ghi report ra file Markdown trong `reports/`.

### Cau hinh

- `config/settings.py`
  - Chua mapping `topic -> RSS sources`.
  - Chua keyword mac dinh cho tung topic.
  - Xay dung time window UTC.
  - Dong goi toan bo cau hinh runtime vao dataclass `Settings`.
  - Neu user nhap topic tuy chinh, file nay van gan RSS theo topic gan nhat co san va them custom keyword vao bo loc.

### Orchestration pipeline

- `src/pipeline/pipeline.py`
  - La file quan trong nhat cua project.
  - Khoi tao collector cho tung bao.
  - Dieu phoi toan bo cac buoc: collect -> filter -> scrape full content -> save processed -> extract keywords -> rank -> summarize -> build report.
  - Co co che incremental fetch:
    - neu da co raw data moi trong cua so hien tai
    - chi fetch RSS moi hon moc do
  - Gop ket qua cuoi cung thanh report Markdown.

### Collectors

- `src/collectors/base_collector.py`
  - Dinh nghia interface chung cho collector.
  - Bat buoc moi collector phai co:
    - `fetch_articles()`
    - `fetch_full_content()`

- `src/collectors/rss_collector.py`
  - Collector co so cho cac nguon RSS.
  - Doc XML RSS bang `urlopen`.
  - Parse tung `<item>` thanh article dict chuan.
  - Chuan hoa `published_at` ve UTC.
  - Dung `min_published_after` de dung som khi gap tin cu.

- `src/collectors/vnexpress.py`
  - Ke thua `RSSCollector`.
  - Chi bo sung logic scrape full article cho VnExpress bang HTML selectors rieng.

- `src/collectors/thanhnien.py`
  - Giong VnExpress, nhung selector duoc viet rieng cho Thanh Nien.

- `src/collectors/tuoitre.py`
  - Giong hai file tren, nhung selector duoc viet rieng cho Tuoi Tre.

Y tuong thiet ke o day la:
- Phan lay danh sach bai viet dung chung qua RSS
- Phan lay full content tach rieng theo tung website vi HTML moi bao khac nhau

### Processors

- `src/processors/filter.py`
  - Loc bai viet theo thoi gian va keyword.
  - Gop `title + content`, clean text, roi kiem tra keyword co xuat hien hay khong.

- `src/processors/keyword_extractor.py`
  - Tokenize du lieu van ban.
  - Tinh keyword noi bat bang mot bien the TF-IDF don gian.
  - Ham `rank_articles()` tinh diem relevance cho moi bai dua tren tong trong so keyword co trong bai.

- `src/processors/summarizer.py`
  - Tao executive summary cho toan bo tap bai viet.
  - Khong tom tat bang model AI trong pipeline chinh.
  - Hien tai summary duoc tao bang rule-based text generation:
    - lay top keywords
    - dem muc do xuat hien
    - ghep thanh doan tong ket ngan

### Utils

- `src/utils/date_utils.py`
  - Parse ngay gio.
  - Chuan hoa datetime ve UTC.
  - Ho tro parse tham so ngay tu CLI.

- `src/utils/text_utils.py`
  - Clean HTML/text.
  - Tokenize van ban.
  - Loai bo mot so stopwords Viet/Anh co ban.

- `src/utils/article_storage.py`
  - Doc/ghi JSON bai viet.
  - Sort bai moi nhat len truoc.
  - Remove duplicate theo URL.
  - Cat danh sach bai theo time window.

- `src/utils/storage_paths.py`
  - Sinh ten file JSON on dinh theo tung nguon.
  - Tach ro raw path va processed path.

### LLM support

- `src/models/llm.py`
  - Chua helper de tang cuong summary/report bang OpenAI API.
  - Hien tai dang la phan mo rong, chua duoc bat trong luong chay chinh cua `main.py` va `NewsPipeline`.
  - Nghia la project van chay duoc hoan toan neu khong co API key.

## Luong du lieu trong project

```text
CLI (main.py)
  -> Settings
  -> NewsPipeline
  -> Collect RSS theo tung source
  -> data/raw/*.json
  -> Filter + scrape full content
  -> data/processed/*.json
  -> Keyword extraction + ranking + summary
  -> reports/weekly_report_*.md
```

## Thu muc output

- `data/raw/`
  - Luu bai lay truc tiep tu RSS

- `data/processed/`
  - Luu bai sau khi loc va bo sung full content

- `reports/`
  - Luu file bao cao Markdown sinh ra sau moi lan chay

## Tom tat kien truc

Neu nhin ngan gon, project nay chia thanh 4 lop:

- `main.py`: nhan lenh tu user
- `config/`: quyet dinh project chay voi topic/time window nao
- `collectors/` + `processors/`: xu ly du lieu
- `pipeline/`: dieu phoi tat ca va tao report

Day la mot thiet ke de hieu, de bao tri, va phu hop voi bai toan thu thap va tong hop tin tuc theo luong batch nho.
