from tkinter import *
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from textblob import TextBlob
import threading

root = Tk()
root.title("Tomato Sentiment")
root.resizable(False, False)

def getURL(movie, page):
    movie = movie.replace(' ', '_')
    return f'https://www.rottentomatoes.com/m/{movie}/reviews?type=&sort=&page={page}'

def extractReviewInfo(movie, maxPages):
    csv_file = open('rotten_tomatoes_scrape.csv', 'w', encoding="utf-8")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Name', 'Publication', 'Review', 'Original Score', 'Polarity', 'Subjectivity'])

    driver = webdriver.Chrome('C:\\Users\Kyle Ruiz\\Documents\Selenium Driver\\chromedriver.exe')

    reviewCount = 0
    positiveReviewCount = 0
    score = ""

    for page in range(1, maxPages):
        url = getURL(movie, page)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        records = soup.find_all('div', {'class': 'row review_table_row', 'data-qa': 'review-item'})
        for record in records:
            try:
                name = record.find('a', class_='unstyled bold articleLink').text
                publication = record.find('em', class_='subtle critic-publication').text
                review = record.find('div', class_='the_review').text.strip()
            except AttributeError:
                reviewCount -= 1
                name = ""
                publication = ""
                review = ""
            rotten = record.find('div', class_='review_icon icon small rotten')
            fresh = record.find('div', class_='review_icon icon small fresh')

            if rotten is None:
                score = "Certified Fresh"
            elif fresh is None:
                score = "Rotten Tomatoes"

            analysis = TextBlob(review)
            polarity = analysis.sentiment.polarity
            subjectivity = analysis.sentiment.subjectivity

            if polarity > 0:
                positiveReviewCount += 1
            reviewCount += 1

            csv_writer.writerow([name, publication, review, score, polarity, subjectivity])
    resultText = f"{round(positiveReviewCount/reviewCount*100, 3)}% via {reviewCount} samples"
    percisionResultLabel.config(text=resultText)
    csv_file.close()
    driver.close()


def analyzeButtonClicked():
    movie = movieTextField.get()
    maxPages = pageTextField.get()
    maxPages = int(maxPages)

    t1 = threading.Thread(target=extractReviewInfo, args=[movie, maxPages])
    t1.start()


movieLabel = Label(root, text="Enter a movie: ", font=("Arial", 12))
pageLabel = Label(root, text="Number of pages: ", font=("Arial", 12))
percisisonLabel = Label(root, text="Positive Percision: ", font=("Arial", 12))
percisionResultLabel = Label(root, text="None", font=("Arial", 12))
movieTextField = Entry(root, width=32, font=("Arial", 12))
pageTextField = Entry(root, width=13, font=("Arial", 12))
analyzeButton = Button(root, text="Analyze", padx=5, pady=5, command=analyzeButtonClicked)

movieLabel.grid(row=0, column=0, sticky="E")
pageLabel.grid(row=1, column=0, sticky="E")
percisisonLabel.grid(row=2, column=0, sticky="E")
movieTextField.grid(row=0, column=1, sticky="W")
pageTextField.grid(row=1, column=1, sticky="W")
percisionResultLabel.grid(row=2, column=1, sticky="W")
analyzeButton.grid(row=3, column=1, sticky="E")

root.geometry("440x110")
root.mainloop()
