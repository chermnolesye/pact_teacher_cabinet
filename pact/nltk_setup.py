import nltk

def download_nltk_resources():
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('punkt_tab')

if __name__ == '__main__':
    download_nltk_resources()