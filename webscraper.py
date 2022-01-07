from datetime import datetime
import pandas as pd
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
# from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from logging_webscraper import logger

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class WebScraper:
    def __init__(self, browser: str = None, headless: bool = True):
        self.headless = headless
        self.browser = browser
        self.driver = self.create_webdriver()
        self.page_text = ''
        self.time_checked = datetime.utcnow()
        self.df = pd.DataFrame()

    def create_webdriver(self):
        logger.info(f'Browser is {self.browser}')
        if self.browser == 'Firefox':
            opts = webdriver.FirefoxOptions()
            if self.headless:
                opts.headless = True
            # self.driver = webdriver.Firefox(GeckoDriverManager().install(), options=opts)
            driver = webdriver.Firefox(options=opts)
        elif self.browser == 'Chrome':
            opts = webdriver.ChromeOptions()
            if self.headless:
                opts.headless = True
            # self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
            driver = webdriver.Chrome(options=opts)
        else:
            driver = None
        return driver

    def load_url(self, url: str):
        logger.info(f'Loading {url}')
        if self.driver:
            # doing this so that I don't navigate back to the original page for semi-automated scraping
            if url not in self.driver.current_url:
                self.driver.get(url)
        else:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36', }
            res = requests.get(url, headers=headers, verify=False)
            if res.ok:
                self.page_text = res.text

    def return_soup(self) -> BeautifulSoup:
        """
        Returns a BeautifulSoup object from the driver page source parsed as HTML
        :return: BeautifulSoup HTML parsed data
        """
        if self.driver:
            return BeautifulSoup(self.driver.page_source, 'html.parser')
        else:
            return BeautifulSoup(self.page_text, 'html.parser')

    def return_element_attrs(self, elem: str):
        soup = self.return_soup()
        all_elems = soup.find_all(elem)
        attr_text = f"{len(all_elems)} instances of {elem} found on page\n"
        for i, el in enumerate(all_elems):
            attr_text += f"{i} - {el.attrs}\n"
        return attr_text

    def clear_dataframe(self):
        self.df = pd.DataFrame()

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
        row_elem = kwargs.get('row_elem', 'tr')
        cell_elem = kwargs.get('cell_elem', 'td')
        header_elem = kwargs.get('header_elem', 'th')
        table_data = []
        if table_attrs is not None:
            table = soup.find(table_elem, attrs=table_attrs)
        elif table_num is not None and table_num.isnumeric():
            table = soup.find_all(table_elem)[int(table_num)]
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
            self.df.drop_duplicates(inplace=True)
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
        if self.driver:
            self.driver.close()
