import sys
import psycopg2
from decimal import Decimal
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QComboBox, QListWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QLineEdit, QHBoxLayout, QPushButton


def fmt(val):
    if isinstance(val, (float, Decimal)):
        return f"{float(val):.2f}"
    return str(val).strip()


class milestone1(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CptS 451 Milestone 2")
        self.setGeometry(100, 100, 1200, 600)
        self.init_ui()
        self.loadStateList()
        self.stateCombo.currentTextChanged.connect(self.stateChanged)
        self.cityList.itemSelectionChanged.connect(self.cityChanged)
        self.zipcodeList.itemSelectionChanged.connect(self.zipcodeChanged)
        self.searchButton.clicked.connect(self.searchClicked)
        self.clearButton.clicked.connect(self.clearClicked)
        self.refreshButton.clicked.connect(self.refreshClicked)
        # self.bnameInput.textChanged.connect(self.getBusinessNames)
        # self.businessList.itemSelectionChanged.connect(self.displayBusinessCity)
        
    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

         # Left panel: State -> City -> Zipcode cascade
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("State"))
        self.stateCombo = QComboBox()
        left_layout.addWidget(self.stateCombo)

        left_layout.addWidget(QLabel("City"))
        self.cityList = QListWidget()
        left_layout.addWidget(self.cityList)

        left_layout.addWidget(QLabel("Zipcode"))
        self.zipcodeList = QListWidget()
        left_layout.addWidget(self.zipcodeList)

        # left_layout.addWidget(QLabel("Search Business by Name"))
        # self.bnameInput = QLineEdit()
        # left_layout.addWidget(self.bnameInput)
        # self.businessList = QListWidget()
        # left_layout.addWidget(self.businessList)
        # left_layout.addWidget(QLabel("City for Business:"))
        # self.cityForBusiness = QLabel("")
        # left_layout.addWidget(self.cityForBusiness)

        # Middle panel: zipcode statistics, top categories, category filter
        middle_layout = QVBoxLayout()
        middle_layout.addWidget(QLabel("Zipcode Statistics"))
        self.numBusinessesLabel = QLabel("# of Businesses:")
        middle_layout.addWidget(self.numBusinessesLabel)
        self.populationLabel = QLabel("Total Population:")
        middle_layout.addWidget(self.populationLabel)
        self.avgIncomeLabel = QLabel("Average Income:")
        middle_layout.addWidget(self.avgIncomeLabel)

        middle_layout.addWidget(QLabel("Top Categories"))
        self.topCategoriesList = QListWidget()
        middle_layout.addWidget(self.topCategoriesList)

        middle_layout.addWidget(QLabel("Filter by Category"))
        self.categoryFilterList = QListWidget()
        middle_layout.addWidget(self.categoryFilterList)

        button_layout = QHBoxLayout()
        self.searchButton = QPushButton("Search")
        button_layout.addWidget(self.searchButton)
        self.clearButton = QPushButton("Clear")
        button_layout.addWidget(self.clearButton)
        middle_layout.addLayout(button_layout)

        # Right panel: search results
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Businesses"))
        self.businessTable = QTableWidget()
        self.businessTable.setColumnCount(7)
        self.businessTable.setHorizontalHeaderLabels(['Business Name', 'Address', 'City', 'Stars', 'Review Count', 'Review Rating', 'Number of Checkins'])
        self.businessTable.setColumnWidth(0, 220)
        self.businessTable.setColumnWidth(1, 180)
        self.businessTable.setColumnWidth(2, 100)
        self.businessTable.setColumnWidth(3, 50)
        self.businessTable.setColumnWidth(4, 90)
        self.businessTable.setColumnWidth(5, 90)
        self.businessTable.setColumnWidth(6, 120)
        right_layout.addWidget(self.businessTable)

        self.refreshButton = QPushButton("Refresh")
        right_layout.addWidget(self.refreshButton)

        popsucc_layout = QHBoxLayout()

        popular_layout = QVBoxLayout()
        popular_layout.addWidget(QLabel("Popular Businesses"))
        self.popularTable = QTableWidget()
        self.popularTable.setColumnCount(4)
        self.popularTable.setHorizontalHeaderLabels(['Business Name', 'Checkins', 'Review Count', 'Popularity Score'])
        self.popularTable.setColumnWidth(0, 180)
        popular_layout.addWidget(self.popularTable)
        popsucc_layout.addLayout(popular_layout)

        successful_layout = QVBoxLayout()
        successful_layout.addWidget(QLabel("Successful Businesses"))
        self.successfulTable = QTableWidget()
        self.successfulTable.setColumnCount(5)
        self.successfulTable.setHorizontalHeaderLabels(['Business Name', 'Longevity (days)', 'Avg Reviewer Fans', 'Avg Reviewer Review Count', 'Success Score'])
        self.successfulTable.setColumnWidth(0, 180)
        successful_layout.addWidget(self.successfulTable)
        popsucc_layout.addLayout(successful_layout)

        right_layout.addLayout(popsucc_layout)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(middle_layout, 2)
        main_layout.addLayout(right_layout, 5)
        central.setLayout(main_layout)


    def executeQuery(self,sql_str, params=None):
        try:
            conn = psycopg2.connect("dbname='yelpdb' user='postgres' host='localhost'") #password comes from pgpass.conf
            cur = conn.cursor()
            cur.execute(sql_str, params)
            conn.commit()
            result = cur.fetchall()
            conn.close()
            return result
        except Exception as db:
            print( f"unable to connect: {db}")
            return []

    def loadStateList(self):
        sql_str = "SELECT distinct state FROM business ORDER BY state;"
        try:
            results = self.executeQuery(sql_str)
            for row in results:
                self.stateCombo.addItem(row[0].strip())
        except: 
            print("Query failed")

    def clearZipcodeDetails(self):
        self.numBusinessesLabel.setText("# of Businesses:")
        self.populationLabel.setText("Total Population:")
        self.avgIncomeLabel.setText("Average Income:")
        self.topCategoriesList.clear()
        self.categoryFilterList.clear()

    def stateChanged(self):
        self.cityList.clear()
        self.zipcodeList.clear()
        self.clearZipcodeDetails()
        self.businessTable.setRowCount(0)
        self.popularTable.setRowCount(0)
        self.successfulTable.setRowCount(0)
        state = self.stateCombo.currentText()
        if not state:
            return
        sql_str = "SELECT DISTINCT city FROM business WHERE TRIM(state) = %s ORDER BY city;"
        try:
            results = self.executeQuery(sql_str, (state,))
            for row in results:
                self.cityList.addItem(row[0].strip())
        except:
            print("Query failed!")

    def cityChanged(self):
        self.zipcodeList.clear()
        self.clearZipcodeDetails()
        self.businessTable.setRowCount(0)
        self.popularTable.setRowCount(0)
        self.successfulTable.setRowCount(0)
        selected = self.cityList.selectedItems()
        if not selected:
            return
        city = selected[0].text()
        state = self.stateCombo.currentText()
        sql_str = "SELECT DISTINCT zipcode FROM business WHERE TRIM(city) = %s AND TRIM(state) = %s ORDER BY zipcode;"
        try:
            results = self.executeQuery(sql_str, (city, state))
            for row in results:
                self.zipcodeList.addItem(row[0].strip())
        except:
            print("Query failed!")

    def zipcodeChanged(self):
        self.clearZipcodeDetails()
        self.businessTable.setRowCount(0)
        self.popularTable.setRowCount(0)
        self.successfulTable.setRowCount(0)
        selected = self.zipcodeList.selectedItems()
        if not selected:
            return
        zipcode = selected[0].text()

        citySelected = self.cityList.selectedItems()
        city = citySelected[0].text() if citySelected else None
        state = self.stateCombo.currentText()

        #zipcode statistics panel
        sql_str = "SELECT (SELECT COUNT(*) FROM business WHERE zipcode = z.zipcode AND TRIM(city) = %s AND TRIM(state) = %s) AS num_businesses, z.population, z.avg_income FROM zipcodedata z WHERE z.zipcode = %s;"
        stats_params = (city, state, zipcode)
        try:
            results = self.executeQuery(sql_str, stats_params)
            if results:
                self.numBusinessesLabel.setText(f"# of Businesses: {results[0][0]}")
                self.populationLabel.setText(f"Total Population: {results[0][1]}")
                self.avgIncomeLabel.setText(f"Average Income: {results[0][2]}")
        except Exception as e:
            print(f"Query failed: {e}")

        #top categories panel + category filter list
        sql_str = "SELECT c.name, COUNT(*) AS business_count " \
                  "FROM business b " \
                  "JOIN business_category bc ON b.business_id = bc.business_id " \
                  "JOIN category c ON c.category_id = bc.category_id " \
                  "WHERE b.zipcode = %s AND TRIM(b.city) = %s AND TRIM(b.state) = %s " \
                  "GROUP BY c.name " \
                  "ORDER BY business_count DESC, c.name;"
        cat_params = (zipcode, city, state)
        try:
            results = self.executeQuery(sql_str, cat_params)
            for row in results:
                self.topCategoriesList.addItem(f"{row[0].strip()} ({row[1]})")
                self.categoryFilterList.addItem(row[0].strip())
        except Exception as e:
            print(f"Query failed: {e}")

    def searchClicked(self):
        self.businessTable.setRowCount(0)
        selected = self.zipcodeList.selectedItems()
        if not selected:
            return
        zipcode = selected[0].text()
        citySelected = self.cityList.selectedItems()
        city = citySelected[0].text() if citySelected else None
        state = self.stateCombo.currentText()
        catSelected = self.categoryFilterList.selectedItems()
        if catSelected:
            category = catSelected[0].text()
            sql_str = "SELECT b.name, b.address, b.city, b.stars, b.review_count, b.reviewrating, b.num_checkins " \
                      "FROM business b " \
                      "JOIN business_category bc ON b.business_id = bc.business_id " \
                      "JOIN category c ON c.category_id = bc.category_id " \
                     "WHERE b.zipcode = %s AND TRIM(b.city) = %s AND TRIM(b.state) = %s AND c.name = %s " \
                      "ORDER BY b.name;"
            params = params = (zipcode, city, state, category)
        else:
            sql_str = "SELECT name, address, city, stars, review_count, reviewrating, num_checkins " \
            "FROM business WHERE zipcode = %s AND TRIM(city) = %s AND TRIM(state) = %s ORDER BY name;"
            params = (zipcode, city, state)
        try:
            results = self.executeQuery(sql_str, params)
            self.businessTable.setRowCount(len(results))
            for rowIdx, row in enumerate(results):
                for colIdx, val in enumerate(row):
                    self.businessTable.setItem(rowIdx, colIdx, QTableWidgetItem(fmt(val)))
        except:
            print("Query failed!")

    def clearClicked(self):
        self.categoryFilterList.clearSelection()
        self.searchClicked()

    def refreshClicked(self):
        self.popularTable.setRowCount(0)
        self.successfulTable.setRowCount(0)
        selected = self.zipcodeList.selectedItems()
        if not selected:
            return
        zipcode = selected[0].text()
        citySelected = self.cityList.selectedItems()
        city = citySelected[0].text() if citySelected else None
        state = self.stateCombo.currentText()

        popular_sql = ("SELECT b.name, b.num_checkins, b.review_count, "
                       "(b.num_checkins - e.expected_checkins)/NULLIF(e.expected_checkins,0) "
                       "+ (b.review_count - e.expected_reviews)/NULLIF(e.expected_reviews,0) AS popularity_score "
                       "FROM Business b JOIN business_expected_stats e ON b.business_id = e.business_id "
                       "WHERE b.zipcode = %s AND TRIM(b.city) = %s AND TRIM(b.state) = %s "
                       "ORDER BY popularity_score DESC NULLS LAST "
                       "LIMIT 10;")
        try:
            results = self.executeQuery(popular_sql, (zipcode, city, state))
            self.popularTable.setRowCount(len(results))
            for rowIdx, row in enumerate(results):
                for colIdx, val in enumerate(row):
                    self.popularTable.setItem(rowIdx, colIdx, QTableWidgetItem(fmt(val)))
        except:
            print("Query failed!")

        successful_sql = ("WITH scored AS ( "
                          "SELECT bl.business_id, b.name, b.zipcode, b.city, b.state, "
                          "bl.longevity_days, rq.avg_reviewer_fans, rq.avg_reviewer_review_count, "
                          "(bl.longevity_days - MIN(bl.longevity_days) OVER()) / NULLIF(MAX(bl.longevity_days) OVER() - MIN(bl.longevity_days) OVER(), 0) "
                          "+ (rq.avg_reviewer_fans - MIN(rq.avg_reviewer_fans) OVER()) / NULLIF(MAX(rq.avg_reviewer_fans) OVER() - MIN(rq.avg_reviewer_fans) OVER(), 0) "
                          "+ (rq.avg_reviewer_review_count - MIN(rq.avg_reviewer_review_count) OVER()) / NULLIF(MAX(rq.avg_reviewer_review_count) OVER() - MIN(rq.avg_reviewer_review_count) OVER(), 0) AS success_score "
                          "FROM business_longevity bl "
                          "JOIN business_reviewer_quality_min10 rq ON bl.business_id = rq.business_id "
                          "JOIN Business b ON b.business_id = bl.business_id "
                          ") "
                          "SELECT name, longevity_days, avg_reviewer_fans, avg_reviewer_review_count, success_score "
                          "FROM scored "
                          "WHERE zipcode = %s AND TRIM(city) = %s AND TRIM(state) = %s "
                          "ORDER BY success_score DESC NULLS LAST "
                          "LIMIT 10;")
        try:
            results = self.executeQuery(successful_sql, (zipcode, city, state))
            self.successfulTable.setRowCount(len(results))
            for rowIdx, row in enumerate(results):
                for colIdx, val in enumerate(row):
                    self.successfulTable.setItem(rowIdx, colIdx, QTableWidgetItem(fmt(val)))
        except:
            print("Query failed!")

    def getBusinessNames(self):
        self.businessList.clear()
        businessname = self.bnameInput.text()
        if not businessname:
            return
        sql_str = "SELECT name FROM business WHERE name ILIKE %s ORDER BY name;"
        try:
            results = self.executeQuery(sql_str, (f'%{businessname}%',))
            for row in results:
                self.businessList.addItem(row[0].strip())
        except:
            print("Query failed")


    def displayBusinessCity(self):
        selected = self.businessList.selectedItems()
        if not selected:
            return
        businessname = selected[0].text()
        sql_str = "SELECT city FROM business WHERE TRIM(name) = %s;"
        try:
            results = self.executeQuery(sql_str, (businessname,))
            if results:
                self.cityForBusiness.setText(results[0][0].strip())
        except:
            print("Query failed")




if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = milestone1()
        window.show()
        sys.exit(app.exec())





    

    
