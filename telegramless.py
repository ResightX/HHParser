from hhparser import scrape
from sqlmanager import manage_data, get_company_data

if __name__ == "__main__":
    try:
        print('Scraping in progress. Please wait...')
        data = scrape()
        manage_data(data[0], data[1])
    except KeyboardInterrupt as ki:
        print('Keyboard interrupt occured. Exitting...')
        exit(0)
