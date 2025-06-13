## 一、專案概述

**名稱**：藥歷資料匯整 (Pharma Data Viewer)

**目標**：透過 WebUI 和 CLI 介面處理病患檢驗及用藥資料，自動化整理 API 回傳的數據，並視覺化於輸出的 html 檔，協助藥師快速瀏覽病歷重點與 AI 建議。

---

## 二、實作方式

* **開發語言/框架**：Python (WebUI + CLI)
* **WebUI**：本地 Web 伺服器界面，支援瀏覽器訪問
* **CLI**：命令列介面，支援批次處理
* **模式**：
  * **Dev Mode**：
    * 顯示詳細偵錯/Log
    * 切換測試與正式 API
  * **Release Mode**：
    * 隱藏偵錯資訊
* **打包**：PyInstaller 產生 Windows exe

---

## 三、介面

* **WebUI (網頁界面)**
  1. **病歷號輸入**：
    * 輸入框（7 碼，不足前補 0）
    * 驗證：必填、格式為 \d{7}
    * 按 Enter 或點擊按鈕啟動查詢
  2. **日期範圍選擇**：
    * 預設：最近 1 個月
    * 快捷：1 週／1 個月／3 個月／6 個月
    * 自訂：日期選擇器  
  5. **匯出按鈕**

* **CLI (命令列介面)**
  * 支援所有 WebUI 功能的命令列參數
  * 批次處理多個病患
  * **過濾參數支援**：
    * `--show-default` / `--no-default` - 控制預設項目顯示
    * `--show-supplementary` / `--no-supplementary` - 控制補充項目顯示  
    * `--show-other` / `--no-other` - 控制其他項目顯示
    * `--filter-preset` - 快速過濾預設（all, default-only, default-supp）
    * CLI 過濾狀態輸出信息

---

## 四、主要功能需求

### 1. 依時間序的檢驗數據 {lab_data}

* **API**：

  * `https://hisapi01.edah.org.tw/pacsrestapi.svc/QueryAllLabData?CharNo={病歷號}&QueryScope=&QueryClass=ABCDEFGHIJK&QStartDate={YYYY/MM/DD}&QEndDate={YYYY/MM/DD}`
* **回傳欄位**：

  * `patnum`: 病歷號
  * `code_desc`: 檢驗類別
  * `testname`: 檢驗名稱
  * `normal_range`: 正常範圍
  * `unit`: 單位
  * `result`: 檢驗結果
  * `reqdatetime`: 中華民國紀年 YYYMMDDHHMM（例如「11007121423」代表西元2021/07/12 14:23）
* **表格欄位**：

  1. 類別 (code\_desc)
  2. 檢驗名稱 (testname)
  3. 正常範圍 (normal\_range + unit)
  4. 日期欄位1 (最新日期)
  5. 日期欄位2 (次新日期)
  6. 依序往後...
* **顯示規則**：

  **過濾控制面板**：
    * 預設項目 (default items) - 預設勾選
    * 補充項目 (supplementary items) - 預設不勾選，需要時展開
    * 其他項目 (other items) - 預設不勾選
    * 項目數量統計顯示
    * 快速過濾按鈕：僅預設項目、預設+補充、所有項目
    * 全選/全不選功能按鈕
  **即時過濾更新**：
    * 過濾狀態變更時即時更新表格顯示
    * 顯示當前過濾統計（顯示 X 項 / 總 Y 項）
  * 依 `code_desc` 分組，顯示分組標題
  * 同一日期結果置於同一欄：
    * 單筆：直接顯示數值
    * 多筆：依 `reqdatetime` 時間排序，一行一筆，格式 `HH:mm: value`
  * 異常值（超出 `normal_range`）以紅色粗體顯示

  * **顯示項目**：
    * add to unit test
    * 顯示規則：有數值才出現欄位，分成預設項目跟補充項目，補充項目平時收起來，需要時再點選展開。不在預設項目也不在補充項目的其他項目不顯示，等到選擇時再全部顯示。
    * 預設項目: BUN
      Creatinine
      eGFR
      NA
      K
      CA
      MG
      AST(GOT) 
      ALT(GPT)
      TBIL
      Albumin
      Lactate(Blood)
      CRP
      前降鈣素原(PCT) 
      WBC
      Neutrophil
      Hb
      PLT
      INR
    * 補充項目: P
      UA
      T4
      TSH
      FE
      Ferritin
      TIBC
      ACR
      UPCR
      HDLC 
      LDL-C
      Total Cholesterol
      TG
      Glucose (AC)
      HbA1c

### 2. 微生物檢驗報告歷程 {microbio_data}

* **API**：`QueryMicrobioData?CharNo={病歷號}&QStartDate={YYYY/MM/DD}&QEndDate={YYYY/MM/DD}`
* **回傳欄位**：

  * `RptDate`: 報告日期 (中華民國紀年 YYY.MM.DD)
  * `RptTime`: 報告時間 (HH:MM:SS)
  * `ChartNo`: 病歷號
  * `SpecName`: 檢體部位/類型 (例如：Blood, Urine, Sputum)
  * `DicName`: 檢查類型 (例如：Blood Culture, Aerobic Culture)
  * `Status`: 報告狀態 (初步/最終)
  * `OrganRptSub`: 培養結果陣列
    * `OrganName`: 菌種名稱或培養結果
    * `RptDate`, `RptTime`: 結果時間
  * `RisRptSub`: 抗藥性測試結果陣列 (包含 antibiotic, MIC, interpretation)
* **表格欄位**：

  1. 檢體類型 (SpecName)
  2. 檢查項目 (DicName)
  3. 培養結果 (OrganName)
  4. 日期欄位1 (最新日期)
  5. 日期欄位2 (次新日期)
  6. 依序往後...
* **顯示規則**：

  * 依 `SpecName`（檢體部位）分組，顯示小節標題
  * 同日結果同欄，多筆依時間排序，格式 `HH:MM: 結果`
  * 抗藥性結果以子表格顯示：Antibiotic / MIC / Interpretation
  * 耐藥性 (R) 結果以紅色粗體標示


### 3. 依時間序的用藥歷程 {drug_data}

* **API**：`QueryMedicationData?CharNo={病歷號}&QStartDate={YYYY/MM/DD}&QEndDate={YYYY/MM/DD}`
* **資料來源**：
  
  * **醫師處方 (現狀藥囑)**：
    * `alise_desc`: 藥品名稱
    * `qty`: 單次劑量
    * `unit_desc`: 劑量單位
    * `cir_code`: 給藥頻率 (BID, TID, Q12H 等)
    * `path_code`: 給藥途徑 (PO, IV, SC 等)
    * `start_date`, `start_time`: 開始時間 (YYYYMMDD, HHMM)
    * `dc_date`, `dc_time`: 停藥時間 (YYYYMMDD, HHMM)
    * `days`: 給藥天數
  
  * **實際給藥記錄 (護理給藥)**：
    * `AliseDesc`: 藥品名稱
    * `Qty`: 實際給予劑量
    * `UnitDesc`: 單位
    * `ConfDate`, `ConfTime`: 給藥確認時間 (YYYYMMDD, HHMM)
    * `ConfOper`: 給藥護理師代碼

* **顯示方式**：**甘特圖 (Gantt Chart)**
  
  * **X軸**：時間軸（日期範圍）
  * **Y軸**：藥品名稱（依類別分組）
  * **橫條**：藥物使用期間
    * 顏色區分：口服藥/注射藥/外用藥
    * 長度：從 start_date 到 dc_date
    * 標示：劑量 + 頻率 (例如：500mg BID)
  * **標記點**：實際給藥時間點
    * 圓點標記護理給藥記錄
    * 顏色對應：正常給藥/延遲給藥
  * **互動功能**：
    * 滑鼠懸停顯示詳細資訊
    * 點擊展開該藥品的詳細給藥記錄
  * **分組顯示**：
    * 抗生素類
    * 心血管用藥
    * 其他藥物

* **技術實作**：
  * 使用 Matplotlib 或 Plotly 製作甘特圖
  * 時間軸處理中華民國紀年轉換
  * 支援縮放和平移功能

### 4. AI 建議內容

* **模型**：OpenAI GPT 系列 (gpt-4 或 gpt-3.5-turbo)
* **接口**：

  * Endpoint: `https://api.openai.com/v1/chat/completions`
  * 提供 API Key
  * 參數：`model`, `messages`, `temperature`, `max_tokens`
* **輸入**：整合檢驗、微生物、用藥資料
* **輸出**：
  * 用藥風險評估摘要
  * 用藥調整建議與理由
  * 選擇詳/略模式

---

## 五、資料匯出功能

* **支援格式**：HTML
* **匯出選項**：包含列號／表頭／病患資訊（可切換）
* **HTML 客戶端過濾功能**：
  * **數據嵌入**：完整實驗室數據嵌入 HTML（包含分類信息）
  * **前端過濾控制**：
    * 複選框控制：預設項目、補充項目、其他項目
    * 快速過濾按鈕：僅預設項目、預設+補充、所有項目
    * 即時統計顯示：總計 X 項｜預設 Y 項｜補充 Z 項｜其他 W 項｜顯示 N 項
  * **JavaScript 實現**：
    * 類似 {drug_data} 的客戶端過濾邏輯
    * 即時表格行隱藏/顯示
    * 過濾狀態保持和切換
    * 空類別區塊自動隱藏
* **模板建議**：

  1. **標頭**：程式名稱、匯出日期、病患基本資訊（姓名、病歷號）
  2. **目錄**：自動產生各功能分頁連結
  3. **檢驗數據表格**：如 WebUI 顯示，依類別分組、日期橫向排列、異常紅粗
  4. **微生物報告**：按採檢部位分小節，列表顯示 Antibiotic、MIC、Interpretation
  5. **用藥數據**：
  6. **AI 建議**：摘要區塊 + 詳細理由
* **匯出流程**：
  * **WebUI**: 一鍵匯出至預設資料夾
  * **CLI**: 給參數後直接執行匯出
  * 匯出完成自動開啟 HTML 對應應用程式
* **Export Manager 整合**：
  * 模板系統更新支援過濾功能
  * 數據預處理包含過濾元數據
  * 文件命名簡化（客戶端過濾）

---

## 六、WebUI 伺服器開發

### WebUI 後端 API 擴展
* **web_gui_server.py** 路由和 API 結構：
  * 添加過濾參數支持的數據處理路由
  * 實現過濾狀態的 API 端點
  * 支援 filter 參數的請求處理

### WebUI 前端界面整合
* **web_gui/index.html** 前端界面：
  * 過濾控制面板整合
  * 前後端過濾狀態同步
  * 即時表格更新功能
  * AJAX 調用過濾 API

---

## 七、開發測試資料

### 測試數據來源
* **位置**：`data/` 目錄
* **格式**：JSON 文件
* **用途**：模擬 API 回傳數據，用於開發和測試

### 測試病歷
#### 病歷號：0350356 ⭐ **主要開發測試用**
* **檢驗數據**：`0350356_檢驗.json` (完整檢驗記錄)
* **微生物報告**：`0350356_微生物報告.json`
* **病毒類報告**：`0350356_病毒類報告.json`
* **現狀藥囑**：`0350356_現狀藥囑.json`
* **護理給藥**：`0350356_護理給藥.json`
* **其他檢查**：一周的檢查清單、放射科報告、染色體報告

#### 病歷號：0550953 ⭐ **主要開發測試用**
* **檢驗數據**：`0550953_檢驗.json` (包含備血等特殊檢驗)
* **微生物報告**：`0550953_微生物報告.json`
* **病毒類報告**：`0550953_病毒類報告.json`
* **現狀藥囑**：`0550953_現狀藥囑.json`
* **護理給藥**：`0550953_護理給藥.json`
* **其他檢查**：一周的檢查清單、放射科報告、染色體報告

### 開發模式設定
* **數據切換**：Dev Mode 時讀取 `data/` 目錄 JSON 文件
* **API 模擬**：Production Mode 時呼叫真實 API
* **測試覆蓋**：
  * 不同數量的檢驗項目
  * 各種微生物檢體類型
  * 多樣化的用藥組合
  * 時間範圍測試

### 單元測試 (Unit Tests)
* **測試框架**：使用 Python `unittest` 或 `pytest`
* **測試覆蓋範圍**：
  * **數據處理函數**：
    * 中華民國紀年轉換 (`convert_roc_date`)
    * JSON 數據解析和驗證
    * 異常值檢測 (`normal_range` 判斷)
    * 藥物分類邏輯
  * **API 模擬**：
    * Mock API 回傳數據格式驗證
    * 錯誤處理測試 (網路異常、無效回應)
    * 不同病歷號的數據完整性
  * **HTML 輸出**：
    * 模板渲染正確性
    * 特殊字符處理 (中文、符號)
    * 表格格式和樣式
  * **甘特圖生成**：
    * 時間軸計算準確性
    * 藥物重疊期間處理
    * 圖片輸出格式驗證

* **測試數據**：
  * **正常案例**：使用 `data/` 目錄現有 JSON 檔案
  * **邊界案例**：
    * 空數據集
    * 單筆記錄
    * 異常大數據量
    * 特殊日期 (跨年、閏年)
  * **異常案例**：
    * 格式錯誤的日期
    * 缺少必要欄位
    * 數值範圍超出預期

* **測試檔案結構**：
  ```
  tests/
  ├── test_data_processing.py      # 數據處理邏輯測試
  ├── test_date_conversion.py      # 日期轉換測試
  ├── test_html_generation.py      # HTML 輸出測試
  ├── test_gantt_chart.py         # 甘特圖生成測試
  ├── test_api_simulation.py      # API 模擬測試
  ├── fixtures/                   # 測試用固定數據
  │   ├── sample_lab_data.json
  │   ├── sample_microbio.json
  │   └── sample_medication.json
  └── test_integration.py         # 整合測試
  ```

* **測試執行**：
  * **開發模式**：`python -m pytest tests/ -v`
  * **CI/CD**：自動化測試流程
  * **覆蓋率報告**：目標 >80% 代碼覆蓋率

* **關鍵測試項目**：
  1. **數據準確性**：確保醫療數據不失真
  2. **日期處理**：中華民國紀年轉換無誤
  3. **異常標示**：檢驗值超標正確標紅
  4. **藥物安全**：用藥時間重疊檢測
  5. **性能測試**：大量數據處理時間
  6. **過濾功能測試**：
     * WebUI 過濾功能測試：前後端數據同步、不同過濾組合表現
     * CLI 過濾功能測試：所有 CLI 過濾參數、導出 HTML 文件質量
     * HTML 過濾測試：客戶端過濾功能、瀏覽器兼容性、大數據集性能

---

## 八、潛在問題與處理

* **JSON UTF-8 BOM**：讀取時過濾 BOM
* **SSL 驗證失敗**：
  * 提供跳過驗證選項(預設)
  * 或匯入自訂憑證

---

## 九、待確認／後續擴充

1. **用藥歷程資料來源與欄位定義**
2. **未來用戶權限或登入需求**（目前無，需預留擴充點）
3. **WebUI 和 CLI 過濾功能的完整整合測試**
4. **HTML 客戶端過濾的跨瀏覽器兼容性測試**
5. **大數據集的過濾性能優化**

---

請檢視以上全版整合內容，如有進一步補充或調整需求，隨時告知！
