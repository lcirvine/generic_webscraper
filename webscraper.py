from datetime import datetime
import pandas as pd
from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
# from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from logging_webscraper import logger


class WebScraper:
    def __init__(self, browser: str = 'Firefox', headless: bool = True):
        self.headless = headless
        if browser == 'Firefox':
            opts = webdriver.FirefoxOptions()
            if self.headless:
                opts.headless = True
            # self.driver = webdriver.Firefox(GeckoDriverManager().install(), options=opts)
            self.driver = webdriver.Firefox(options=opts)
        elif browser == 'Chrome':
            opts = webdriver.ChromeOptions()
            if self.headless:
                opts.headless = True
            # self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
            self.driver = webdriver.Chrome(options=opts)
        self.time_checked = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
        self.df = pd.DataFrame()

    def load_url(self, url: str):
        if url not in self.driver.current_url:
            logger.info(f'Loading {url}')
            self.driver.get(url)

    def return_soup(self) -> BeautifulSoup:
        """
        Returns a BeautifulSoup object from the driver page source parsed as HTML
        :return: BeautifulSoup HTML parsed data
        """
        return BeautifulSoup(self.driver.page_source, 'html.parser')

    def parse_table(self, url: str, include_links: bool,  **kwargs):
        """
        Parses the table identified by the table attributes into a pandas dataframe
        :return: pandas dataframe of table
        """
        self.load_url(url)
        soup = self.return_soup()
        table_elem = kwargs.get('table_elem', 'table')
        table_attrs = kwargs.get('table_attrs')
        table_num = kwargs.get('table_num')
        if table_num is not None and table_num.isnumeric():
            table_num = int(table_num)
        else:
            table_num = None
        row_elem = kwargs.get('row_elem', 'tr')
        cell_elem = kwargs.get('cell_elem', 'td')
        header_elem = kwargs.get('header_elem', 'th')
        table_data = []
        if table_attrs is not None:
            table = soup.find(table_elem, attrs=table_attrs)
        elif table_num is not None:
            table = soup.find_all(table_elem)[table_num]
        else:
            table = soup.find(table_elem)
        if table is not None:
            for row in table.find_all(row_elem):
                cells = [c.text.strip() for c in row.find_all(cell_elem)]
                if include_links:
                    for link in row.find_all('a'):
                        cells.append(link['href'])
                if len(cells) > 1:
                    table_data.append(cells)
            cols = [c.text.strip() for c in table.find_all(header_elem)]
            df_new = pd.DataFrame(table_data)
            if len(cols) == len(df_new.columns):
                df_new.columns = cols
            self.df = pd.concat([self.df, df_new])
        else:
            logger.info(f"Unable to find {table_elem} with attributes {table_attrs} or number {table_num}")
            tables = soup.find_all(table_elem)
            for i, tbl in enumerate(tables):
                logger.info(f"{i} - {tbl.attrs}")

    def return_df(self) -> pd.DataFrame:
        return self.df

    def close(self):
        """
        Closes the browser window, don't forget to close when using a headless browser!
        :return: None
        """
        self.driver.close()
