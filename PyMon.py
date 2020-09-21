import sys
import FinanceDataReader as fdr
import time
import datetime as dt
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


# 코스피 레버리지, 코스닥 레버리지, 코스피 인버스, 코스닥 인버스
tickers = ["122630", "233740", "252670", "251340"]

start_date = dt.datetime(2020, 9, 1).strftime('%Y-%m-%d')
#end_date = dt.datetime.today().strftime('%Y-%m-%d')
end_date = dt.datetime(2020, 9, 18).strftime('%Y-%m-%d')

form_class = uic.loadUiType("leverage.ui")[0]


class Worker(QThread):
     finished = pyqtSignal(dict)

     def run(self):
         while True:
             data = {}

             for ticker in tickers:
                 data[ticker] = self.get_market_infos(ticker)

             self.finished.emit(data)
             time.sleep(2)

     def get_market_infos(self, ticker):

         try:
             day_df = fdr.DataReader(ticker, start_date, end_date)
             ma5 = day_df['Close'].rolling(5).mean()
             last_ma5 = ma5[-2]
             price = day_df['Close'][-1]
             print("price: " + price)

             state = None
             if price > last_ma5:
                 state = "상승장"
             else:
                 state = "하락장"

             return price, last_ma5, state
         except:
             return None, None, None


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.tableWidget.setRowCount(len(tickers))
        self.worker = Worker()
        self.worker.finished.connect(self.update_table_widget)
        self.worker.start()


    @pyqtSlot(dict)
    def update_table_widget(self, data):
        try:
            for ticker, infos in data.items():
                index = tickers.index(ticker)
                self.tableWidget.setItem(index, 0, QTableWidgetItem(ticker))
                self.tableWidget.setItem(index, 1, QTableWidgetItem(str(infos[0])))
                self.tableWidget.setItem(index, 2, QTableWidgetItem(str(infos[1])))
                self.tableWidget.setItem(index, 3, QTableWidgetItem(str(infos[2])))
        except:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    app.exec_()