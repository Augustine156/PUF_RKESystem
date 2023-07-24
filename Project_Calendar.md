# 這是關於專題製作的日誌...

## 7/3

1. 今天將hackrf one接到Mac上，安裝好驅動並且使用URH這款SDR（software define radio），確定儀器沒有損壞，可以偵測到不同頻率。
   - 但是呢，Augstine發現到，藍芽有使用到跳頻（Frequency Hopping）這項技術，這會導致一則訊息會被拆分成多段，並使用特定一段的頻率來傳送。
   - 這會將我們還原訊號的難度“大大大”幅度增加，而且URH看起來一次只能接收單一頻率的訊號，無法完整接收跳頻技術的所有訊息。除此之外，要把藍芽訊號還原成原本的訊息甚至需要用到特定的演算法來執行，這個也非常麻煩。
2.  因此呢，我們決定改用無線電頻率（RF, 433MHz）來作為專題的通訊協定。RF只用單一頻率傳送訊號，這會讓實作難度降低，吧？
   - 因此需要添加下列器材：[Raspberry Pi RF Transceiver](https://www.adafruit.com/product/4075)，[Antenna](https://greatscottgadgets.com/ant500/)，[Wire](https://www.adafruit.com/product/851)。申請書由Yuuta負責，內容包含購買理由，商品詳情，專題進度等等。
3.	URH軟體可以偵測不同頻率的訊號，analog->binary signal，也可以查看不同波形之間的差異在哪裡。


## 7/4

1. 今天研究了一下，擷取到訊號後，應該要怎麼擷取特徵（feature extraction）。這部分就回去把這部分的論文看了看。
 	  - 在收到訊號之後呢，要先對訊號做前處理（pre processing），之後再來做特徵擷取。論文提到的前處理步驟，全部交由GnuRadio這款SDR去處理了，似乎沒有實做任何的程式碼；然後特徵擷取的部分，則是採用了少數特徵(frequency peak...)來當作分類標準而已。
    - 分類演算法有提到SVM和KNN。
    - 但是呢，URH收到的訊號會變成binary signal啊!一堆010101要怎麼找出特徵勒，我沒有其他參數要怎麼辦呢？
      - 我試著找“如何從二進制訊號中擷取特徵的方法”的相關資料（關鍵字：hackrf one, urh, rf, python），但資料不多。目前是在想是不是根本就不能從一堆0101裡面擷取特徵？
2. 試著在Windows安裝hackrf one，URH和GunRadio，看起來是能跑的，但是URH的介面有點奇怪。
3. 目前的問題應該是：我收到訊號了，但是要把訊號轉成什麼形式，來去做前處理和分類演算法呢？---（友泰找到了答案）

## 7/5 - 7/16
1. 教授重新訂定了進度表，雖然有安排到改良系統的部分，但我們評估可能截稿時間到也只能做到GUI而已。做不完再說，專題先過最重要。問問題問得太爛了，有待加強。
2. 雖然Paper用的是GnuRadio，但那個真的不大會用。操作不難，難在要對“訊號處理”有相當的概念。這不是我等所能企及的高度。MatLab好像也可以用，先當作備案來使用。
3. 現在是自己寫code來處理：從URH搜集來的訊號，儲存成.complex檔案。再來寫code處理.complex。

## 7/18
1. Paper裡面選擇的特徵，像是SRB和Spectral Brightness，會用到noise：但是noise已經被URH處理掉了，所以無法獲得。而Spectral Brightness需要threshold：這似乎是Paper在做的時候選取一個區段的頻率來接收訊號才會設定的條件，我們...應該不用吧？排除無法使用的特徵，在採用其他特徵當作train data好了。
2. 今天有把RMS Normalization處理好：如果要避免運算造成的overflow，那就捨棄掉科學記號的"e"，只保留real number的部分。雖然不知道這樣會不會讓訓練結果出大差錯。
3. 要避免無法運算的nan，就事先把nan值刪除再去做計算。

問題：real number 和 imaginary number，是不是只要取real number來作為計算來源就好了呢？
